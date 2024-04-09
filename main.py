import argparse
import asyncio
import copy
import json
import os
from os import path
import random
import shutil
import signal
import subprocess
import time
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
import traceback
import subprocess
import coverage


def random_key(dictionary):
    return random.choice(list(dictionary.keys()))


# def is_interesting(response_payload, status_code):
#     """Check if the response indicates a potential error or contains sensitive information."""
#     # Check if the status code indicates a server error
#     if status_code == None:
#         return False
#     status_code = int(status_code)
#     if status_code >= 300:
#         print("Found a potential server error.")
#         return True

#     # Check for indicators of errors or sensitive information in the response
#     error_indicators = ["exception", "error", "unhandled", "failure"]
#     sensitive_info_indicators = ["password", "username", "private key", "API key"]

#     # Check for error indicators
#     if any(indicator in response_payload.lower() for indicator in error_indicators):
#         print("Found a potential error indicator in the response.")
#         return True

#     # Check for sensitive information indicators
#     if any(
#         indicator in response_payload.lower() for indicator in sensitive_info_indicators
#     ):
#         print("Found potential sensitive information in the response.")
#         return True


#     return False
async def get_latest_file(directory):
    """
    Returns the latest modified file in the specified directory.
    """
    files = []
    for file_name in os.listdir(directory):
        file_path = path.join(directory, file_name)
        if path.isfile(file_path):
            files.append((path.getmtime(file_path), file_path))

    if not files:
        return None
    latest_file = max(files, key=lambda x: x[0])[1]
    return latest_file


# def get_coverage_for_file(filename):
#     """
#     Retrieve coverage data for a specified file from the .coverage data file.
#     Returns a list of line numbers that have been covered.
#     """
#     try:
#         cov = coverage.Coverage()
#         cov.load()
#         file_coverage = cov.get_data().lines(filename)
#         return file_coverage
#     except coverage.CoverageException:
#         print(f"No coverage information found for file: {filename}")
#         return None
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")
#         return None


async def get_coverage_data():
    """
    Retrieves coverage data without combining data files.
    Returns a dictionary with file paths as keys and coverage data as values.
    """
    # Example usage
    latest_file_path = await get_latest_file("./coverages")

    cov = coverage.Coverage(
        data_file=latest_file_path, config_file="./.coveragerc", auto_data=True
    )

    cov.load()
    cov_data = cov.get_data()
    coverage_dict = {}

    for filename in cov_data.measured_files():
        lines = cov_data.lines(filename)
        coverage_dict[filename] = lines
    return coverage_dict


async def has_new_coverage(total_coverage_data: dict, current_coverage_data: dict):
    is_interesting = False
    """Compare old and new coverage data to determine if any new lines of code are covered, and updates the total coverage data"""
    for file, current_cover in current_coverage_data.items():
        previous_cover = total_coverage_data.get(file, [])
        c = list(filter(lambda x: x not in previous_cover, current_cover))
        # If the current coverage is greater than the previous coverage, a new line of code is considered covered
        if len(c) != 0:
            combined = list(set(previous_cover) | set(current_cover))
            is_interesting = True
            total_coverage_data[file] = combined
    return is_interesting


async def is_interesting(total_coverage_data, current_coverage_data):
    """
    Check if the response indicates a potential error, contains sensitive information,
    or if new coverage was detected.
    """
    # # Check if the status code is None or non-standard for successful responses
    # if status_code is None or not (200 <= int(status_code) < 300):
    #     print("Found a non-successful status code.")
    #     return True

    # # Lowercase payload for case-insensitive searching
    # lower_payload = response_payload.lower()

    # # Check for indicators of errors or sensitive information in the response
    # error_indicators = ["exception", "error", "unhandled", "failure", "traceback"]
    # sensitive_info_indicators = ["password", "username", "private key", "API key", "secret"]

    # # Check for error indicators
    # if any(indicator in lower_payload for indicator in error_indicators):
    #     print("Found a potential error indicator in the response.")
    #     return True

    # # Check for sensitive information indicators
    # if any(indicator in lower_payload for indicator in sensitive_info_indicators):
    #     print("Found potential sensitive information in the response.")
    #     return True

    # Check for new coverage
    new_coverage = await has_new_coverage(total_coverage_data, current_coverage_data)
    if new_coverage:
        print("New code coverage detected, which is interesting.")
        return True
    # No indicators of interest found
    return False


async def choose_next_method(SeedQ, FailureQ):
    path = random_key(SeedQ)
    if SeedQ[path] == {}:
        SeedQ.pop(path)
        return None, None

    if path not in FailureQ:
        FailureQ[path] = {}
    method = random_key(SeedQ[path])
    if method not in FailureQ[path]:
        FailureQ[path][method] = {}
    return path, method


async def mutate_openapi(original_input):
    muatated_input = dict()
    for x in original_input:
        muatated_input[x] = copy.deepcopy(original_input[x])
        if muatated_input[x]["type"] == "integer":
            muatated_input[x]["value"] = mutation.random_byte(
                int(muatated_input[x]["value"])
            )
        else:
            # payload[x]["value"] = "".join(
            #     random.choices(
            #         "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890",
            #         k=random.randint(
            #             payload[x]["min_length"], payload[x]["max_length"]
            #         ),
            #     )
            # )
            muatated_input[x]["value"] = mutation.random_byte(
                muatated_input[x]["value"]
            )
    return muatated_input


async def add_to_SeedQ(SeedQ, path, method, mutated_input_seed):
    SeedQ[path][method].append(mutated_input_seed)


async def seed_and_mutate_ble(SeedQ: dict):
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


async def initalize():
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

    if args.arg1 not in ["coap", "http", "ble"]:
        raise ValueError("Invalid protocol")
    # Check if the --file argument is provided
    if args.file and args.arg1 != "ble":
        # Use the value of the --file argument in the parse function
        grammar = parse(args.file)
        url = grammar.servers[0]
    elif args.arg1 == "ble":
        grammar = None
        url = None
    else:
        raise ValueError("no file argument provided")

    match args.arg1:

        case "coap":
            client = COAPClient(url.url)
            SeedQ = parse_openapi(grammar)

        case "http":
            client = DjangoClient(url.url)
            SeedQ = parse_openapi(grammar)

        case "ble":
            raise ValueError("BLE not implemented")
            client = BLEClient(9000)
            await client.initalize_transport()
            SeedQ = await client.get_services()

        case _:
            raise ValueError("Invalid protocol")
    no_coverage = args.nocoverage
    # load all examples/inputs into SeedQ
    # select random path and method in grammar
    total_coverage_data = {}
    return SeedQ, FailureQ, client, no_coverage, total_coverage_data, args


async def main():
    SeedQ, FailureQ, client, no_coverage, total_coverage_data, args = await initalize()
    try:
        server_process = await client.call_process("main_program")
        await asyncio.sleep(1)
    except Exception as e:
        print(e + " " + "Not able to run server, please set --no-coverage")
        raise e
    try:
        while SeedQ:
            # AssignEnergy
            if args.arg1 == "coap" or args.arg1 == "http":
                path, method = await choose_next_method(SeedQ, FailureQ)
                if path == None and method == None:
                    continue
                # Choose input
                if len(SeedQ[path][method]) == 0:
                    original_input = {}
                else:
                    original_input = random.choice(SeedQ[path][method])
            elif args.arg1 == "ble":
                # TODO choose next service/charactistics to fuzz
                original_input = await seed_and_mutate_ble(SeedQ, FailureQ)

            energy = assign_energy.AssignEnergy(original_input)
            for _ in range(energy):

                # For Django and Coap
                if args.arg1 == "coap" or args.arg1 == "http":
                    mutated_input_seed = await mutate_openapi(original_input)
                    mutated_input = {}
                    for x in mutated_input_seed:
                        mutated_input[x] = mutated_input_seed[x]["value"]
                    # print(mutated_input)
                    # print(path)
                    # print(method)
                    print("Sending payload...")
                    response_payload, status_code = await client.send_payload(
                        mutated_input, path, method
                    )

                    # Check if the process has terminated
                    if no_coverage == False:
                        if server_process.poll() is not None:
                            print("Server crashed/timeout! Adding to the FailureQ.")
                            if status_code not in FailureQ[path][method]:
                                FailureQ[path][method][status_code] = []
                            FailureQ[path][method][status_code].append(
                                (mutated_input_seed, response_payload)
                            )
                            server_process = await client.call_process("main_program")

                    # IsInteresting
                    await asyncio.sleep(1)
                    current_coverage_data = await get_coverage_data()
                    if await is_interesting(
                        total_coverage_data,
                        current_coverage_data,
                    ):
                        # Add to SeedQ
                        await add_to_SeedQ(SeedQ, path, method, mutated_input_seed)

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
                    print(SeedQ)
                    driver = client.send_payload(inputs, path, method)
                    zephyr = await client.call_process()
                    response_payload, status_code = await driver
                    zephyr.terminate()
                    # TODO add in isinteresting for SeedQ and FailureQ

    except KeyboardInterrupt as e:
        print(e)

    except Exception as e:
        print(f"{traceback.format_exc()}")

    finally:
        try:
            print("\nShutting Down Server! please wait...")
            server_process.send_signal(signal.SIGINT)
            await asyncio.sleep(3)
            pass
        except:
            pass
        log = ""
        for x in FailureQ:
            log += x + ":\n"
            for y in FailureQ[x]:
                for z in FailureQ[x][y]:
                    print(f"code:{y}, status code: {z}, no = {len(FailureQ[x][y][z])}")
                    log += (
                        f"code:{y}, status code: {z}, no = {len(FailureQ[x][y][z])}\n"
                    )
        with open("SeedQ.json", "w") as json_file:
            json.dump(SeedQ, json_file)
        with open("FailureQ.json", "w") as json_file:
            json.dump(FailureQ, json_file)
        return
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
    asyncio.run(main())
    # file = asyncio.run(get_latest_file("./coverages"))
    # os.remove(file)
    subprocess.run(["coverage", "combine", "--rcfile=./.coveragerc"])
    subprocess.run(["coverage", "report"])

    print("removing htmlcov...")
    try:
        shutil.rmtree("./htmlcov")
    except:
        pass
    print("generating htmlcov...")
    subprocess.run(["coverage", "html"])
