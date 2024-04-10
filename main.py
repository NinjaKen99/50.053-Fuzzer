import argparse
import asyncio
import copy
import json
import os
from os import path
from pprint import pprint
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
from openapiparser import parse_new_openapi, parse_openapi, Schema, Object, Property
from coverages import *
from zephyr.input import BLEClient
from bumble.gatt import Service, Characteristic, Descriptor
from bumble.gatt_client import ServiceProxy, CharacteristicProxy, DescriptorProxy
from bumble.att import Attribute
import traceback
import subprocess
import coverage


def random_key(dictionary):
    return random.choice(list(dictionary.keys()))

async def choose_next_seed(SeedQ:dict, FailureQ:dict):
    path = random_key(SeedQ)
    if SeedQ[path]["methods"] == {}:
        SeedQ.pop(path)
        return None, None

    if path not in FailureQ:
        FailureQ[path] = {}
        for method in SeedQ[path]["methods"]:
            FailureQ[path][method] = {}
    seed = random.choice(SeedQ[path]["seeds"])
    return path, seed


async def mutate_openapi(original_input, schema: Object):
    muatated_input = dict()
    if schema.type.value == "object":
        for x in original_input:
            i: Property
            for i in schema.properties:
                if x == i.name:
                    muatated_input[x] = copy.deepcopy(original_input[x])
                    if i.schema.type == "integer":
                        # muatated_input[x] = mutation.random_byte(
                        #     int(muatated_input[x])
                        # )
                        muatated_input[x] = int(muatated_input[x])
                    else:
                        # muatated_input[x] = mutation.random_byte(
                        #     muatated_input[x]
                        # )
                        muatated_input[x] = str(muatated_input[x])
                    break
    elif schema.type.value == "string":
        muatated_input = copy.deepcopy(original_input)
        muatated_input["string"] = mutation.random_byte(muatated_input["string"])
    return muatated_input


async def add_to_SeedQ(SeedQ, path, mutated_input_seed):
    SeedQ[path]["seeds"].append(mutated_input_seed)


async def seed_and_mutate_ble(SeedQ: dict):
    attribute = random_key(SeedQ)
    return random.choice(SeedQ[attribute]["value"]), None, SeedQ[attribute]["object"]
    


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
            SeedQ = parse_new_openapi(grammar)

        case "http":
            client = DjangoClient(url.url)
            SeedQ = parse_new_openapi(grammar)

        case "ble":
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
        await asyncio.sleep(2)
    except Exception as e:
        print(e + " " + "Not able to run server, please set --no-coverage")
        raise e
    try:
        while SeedQ:
            # AssignEnergy
            if args.arg1 == "coap" or args.arg1 == "http":
                if args.arg1 == "http":
                    await client.login("example", "example")
                path, seed = await choose_next_seed(SeedQ, FailureQ)
                if path == None:
                    continue
            elif args.arg1 == "ble":
                # TODO choose next service/charactistics to fuzz
                seed, path, method = await seed_and_mutate_ble(SeedQ)
                seed = {"byte": seed}
            energy = assign_energy.AssignEnergy(seed)
            for _ in range(energy):

                # For Django and Coap
                if args.arg1 == "coap" or args.arg1 == "http":
                    mutated_input_seed = await mutate_openapi(seed, SeedQ[path]["schema"])
                    # print(mutated_input)
                    # print(path)
                    # print(method)
                    for method in SeedQ[path]["methods"]:
                        response_payload, status_code = await client.send_payload(
                            mutated_input_seed, path, method, SeedQ[path]["schema"]
                        )
                        await asyncio.sleep(0.5)
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
                                print("Server Restarting!")
                                await asyncio.sleep(2)

                        # IsInteresting
                        current_coverage_data = await get_coverage_data()
                        if await is_interesting(
                            total_coverage_data,
                            current_coverage_data,
                        ):
                            # Add to SeedQ
                            await add_to_SeedQ(SeedQ, path, mutated_input_seed)

                elif args.arg1 == "ble":
                    driver = client.send_payload(seed, path, method)
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
        if args.arg1 == "coap" or args.arg1 == "http":
            for path in SeedQ:
                SeedQ[path].pop("schema")

        with open("SeedQ.json", "w") as json_file:
            json.dump(SeedQ, json_file)
        with open("FailureQ.json", "w") as json_file:
            json.dump(FailureQ, json_file)
        await asyncio.sleep(3)
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
