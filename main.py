import argparse
import asyncio
import json
import os
import random
import shutil
import signal
import subprocess
from coap.input import COAPClient
from django.input import DjangoClient
import assign_energy
from mutations import mutation
from openapi_parser import parse
from openapiparser import parse_openapi


def random_key(dictionary):
    return random.choice(list(dictionary.keys()))


def is_interesting(response_payload, status_code):
    """Check if the response indicates a potential error or contains sensitive information."""
    # Check if the status code indicates a server error
    if status_code == None:
        return False
    status_code = int(status_code)
    if status_code >= 300:
        print("Found a potential server error.")
        return True

    # Check for indicators of errors or sensitive information in the response
    error_indicators = ["exception", "error", "unhandled", "failure"]
    sensitive_info_indicators = ["password", "username", "private key", "API key"]

    # Check for error indicators
    if any(indicator in response_payload.lower() for indicator in error_indicators):
        print("Found a potential error indicator in the response.")
        return True

    # Check for sensitive information indicators
    if any(
        indicator in response_payload.lower() for indicator in sensitive_info_indicators
    ):
        print("Found potential sensitive information in the response.")
        return True

    return False


def choose_next(SeedQ):
    return random.choice(SeedQ)


async def main():

    # Specify the directory where you want to delete files
    directory = "./coverages"

    # List all files in the directory
    files = os.listdir(directory)

    # Filter files that start with ".coverage"
    coverage_files = [file for file in files if file.startswith(".coverage")]
    # coverage_files.remove(".coverage")
    # Delete each file
    for file in coverage_files:
        file_path = os.path.join(directory, file)
        os.remove(file_path)
    try:

        FailureQ = {}
        parser = argparse.ArgumentParser(description="Description of your script")
        parser.add_argument("arg1", type=str, help="Protocol of Request")
        parser.add_argument("arg2", type=str, help="OpenAPI 3.03 json file")
        parser.add_argument(
            "--nocoverage", action="store_true", help="Disable code coverage"
        )
        args = parser.parse_args()
        try:
            grammar = parse(args.arg2)

        except Exception as e:
            print(e)
            exit(1)
        # with open(args.arg3) as f:
        #     # Load the JSON data
        #     dictionary = json.load(f)

        url = grammar.servers[0]

        match args.arg1:

            case "coap":
                client = COAPClient(url.url)

            case "http":
                client = DjangoClient(url.url)

            case _:
                raise ValueError("Invalid protocol")
        no_coverage = args.nocoverage

        # load all examples/inputs into SeedQ
        # select random path and method in grammar

        SeedQ = parse_openapi(grammar)
        await asyncio.sleep(2)
        while SeedQ:
            # TODO ChooseNext from SeedQ

            path = random_key(SeedQ)
            if SeedQ[path] == {}:
                SeedQ.pop(path)
                continue

            if path not in FailureQ:
                FailureQ[path] = {}

            method = random_key(SeedQ[path])

            if method not in FailureQ[path]:
                FailureQ[path][method] = {}
            # AssignEnergy
            energy = assign_energy.AssignEnergy(SeedQ[path][method])
            for _ in range(energy):
                # TODO mutate input
                payload = SeedQ[path][method]
                context = method
                inputs = dict()
                for x in payload:
                    if payload[x]["type"] == "integer":
                        payload[x]["value"] = mutation.random_byte(
                            int(payload[x]["value"])
                        )
                        inputs[x] = payload[x]["value"]
                    else:
                        # payload[x]["value"] = mutation.random_byte(payload[x]["value"])
                        payload[x]["value"] = "".join(
                            random.choices(
                                "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
                                k=random.randint(
                                    payload[x]["min_length"], payload[x]["max_length"]
                                ),
                            )
                        )
                        inputs[x] = payload[x]["value"]

                    context += f", {x}={payload[x]}"
                if no_coverage == False:
                    try:
                        server_process = await client.call_process(context)
                    except Exception as e:
                        print(e + " " + "Not able to run server, please set --no-coverage")
                        raise e
                    await asyncio.sleep(2)
                # pid = server_process.pid
                response_payload, status_code = await client.send_payload(
                    inputs, path, method
                )
                # Check if the process has terminated
                if no_coverage == False:
                    if server_process.poll() is not None:
                        pass
                        print("Server crashed!")
                    else:
                        server_process.send_signal(signal.SIGINT)
                        await asyncio.sleep(1)

                # backendcov = coverage.CoverageData("./.coverage")
                # backendcov.read()
                # print(backendcov.measured_files())
                # print(backendcov.measured_contexts())
                # for x in backendcov.measured_files():
                #     print(backendcov.lines(x))

                # cov.stop()
                # print(cov.get_data().measured_files())
                # for x in cov.get_data().measured_files():
                #     print(x)
                #     print(cov.get_data().lines(x))
                # TODO isInteresting
                if is_interesting(response_payload, status_code):
                    print("Interesting finding! Adding to the FailureQ.")
                    if status_code not in FailureQ[path][method]:
                        FailureQ[path][method][status_code] = []
                    FailureQ[path][method][status_code].append(
                        (payload, response_payload)
                    )
    except Exception as e:
        print(f"An error occurred: {e}")
        raise e
    finally:
        try:
            server_process.terminate()
            pass
        except:
            pass
        log = ""
        # print("FailureQ: ", FailureQ)
        for x in FailureQ:
            # print(x)
            log += x + ":\n"
            for y in FailureQ[x]:
                for z in FailureQ[x][y]:
                    print(f"code:{y}, status code: {z}, no = {len(FailureQ[x][y][z])}")
                    log += (
                        f"code:{y}, status code: {z}, no = {len(FailureQ[x][y][z])}\n"
                    )
        with open("log.json", "w") as json_file:
            json.dump(FailureQ, json_file)
        with open("log.txt", "w") as file:
            file.write(log)
        print("Exiting Fuzzer...")
        await asyncio.sleep(5)

    """
    Step 1: Compile Openapi json to a readable format
    Step 2: Randomly chooose a path
    Step 3: retieve seed from dictionary.json
    Step 4: Do fuzzing
    
    t = ChooseNext(SeedQ)
    E(t) = AssignEnergy(t)
    for i from 1 to E(t) do
        t` = MutateInput(t)
        if (t` reveals a bug/crash) then
            add t` to FailureQ
        else if Isinteresting(Q)
            add t'' to SeedQ
    """


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt as e:
        subprocess.run(["coverage", "combine"])
        subprocess.run(["coverage", "report"])

        print("removing htmlcov...")
        try:
            shutil.rmtree("./htmlcov")
        except:
            pass
        print("generating htmlcov...")
        subprocess.run(["coverage", "html"])
