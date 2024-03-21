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
from zephyr.input import BLEClient
from bumble.gatt import Service, Characteristic, Descriptor
from bumble.gatt_client import ServiceProxy, CharacteristicProxy, DescriptorProxy
from bumble.att import Attribute


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


async def seed_and_mutate_openapi(SeedQ: dict, FailureQ: dict):
    # TODO ChooseNext from SeedQ
    path = random_key(SeedQ)
    if SeedQ[path] == {}:
        SeedQ.pop(path)
        return None, None, None, None

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
                payload[x]["value"] = mutation.random_byte(int(payload[x]["value"]))
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
    return inputs, path, method, context


async def seed_and_mutate_ble(SeedQ: dict, FailureQ: dict):
    service = random_key(SeedQ["services"])
    if SeedQ["services"][service]["characteristics"] == {}:
        SeedQ["services"].pop(service)
        return None, None, None, None
    characteristic = random_key(SeedQ["services"][service]["characteristics"])
    if (
        Attribute.Permissions.WRITEABLE
        == SeedQ["services"][service]["characteristics"][characteristic]["permissions"]
    ):
        # Generate a random byte (integer between 0 and 255)
        random_byte = random.randint(0, 255)

        # If you need to convert it to a bytes object, you can use the bytes() constructor
        random_byte_as_bytes = bytes([random_byte])
        # input = SeedQ["services"][service]["characteristics"][characteristic]["value"]
        input = random_byte_as_bytes
        return (
            input,
            SeedQ["services"][service]["object"],
            SeedQ["services"][service]["characteristics"][characteristic]["object"],
            {},
        )
    else:
        return None, None, None, None


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
        parser.add_argument(
            "--file", type=str, help="OpenAPI 3.03 json file", required=False
        )
        parser.add_argument(
            "--nocoverage", action="store_true", help="Disable code coverage"
        )
        args = parser.parse_args()
        # Check if the --file argument is provided
        if args.file:
            # Use the value of the --file argument in the parse function
            grammar = parse(args.file)
            url = grammar.servers[0]
        else:
            print("No --file argument provided.")
        # with open(args.arg3) as f:
        #     # Load the JSON data
        #     dictionary = json.load(f)

        match args.arg1:

            case "coap":
                client = COAPClient(url.url)
                SeedQ = parse_openapi(grammar)

            case "http":
                client = DjangoClient(url.url)
                SeedQ = parse_openapi(grammar)

            case "ble":
                client = BLEClient(9000)
                await client.initalize_transport()
                SeedQ = await client.get_services()

            case _:
                raise ValueError("Invalid protocol")
        no_coverage = args.nocoverage

        # load all examples/inputs into SeedQ
        # select random path and method in grammar

        await asyncio.sleep(2)
        while SeedQ:
            if args.arg1 == "coap" or args.arg1 == "http":
                inputs, path, method, context = await seed_and_mutate_openapi(
                    SeedQ, FailureQ
                )
                if (
                    inputs == None
                    and path == None
                    and method == None
                    and context == None
                ):
                    continue
                elif no_coverage == False:
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

            elif args.arg1 == "ble":
                inputs, path, method, context = await seed_and_mutate_ble(
                    SeedQ, FailureQ
                )
                if (
                    inputs == None
                    and path == None
                    and method == None
                    and context == None
                ):
                    continue
                driver = client.send_payload(inputs, path, method)
                zephyr = await client.call_process()
                response_payload, status_code = await driver
                zephyr.terminate()
                
                
                

 

            # TODO isInteresting
            if is_interesting(response_payload, status_code):
                print("Interesting finding! Adding to the FailureQ.")
                if status_code not in FailureQ[path][method]:
                    FailureQ[path][method][status_code] = []
                FailureQ[path][method][status_code].append((inputs, response_payload))
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
