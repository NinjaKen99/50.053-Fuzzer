import argparse
import asyncio
import copy
from datetime import datetime
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
from initalize import init_parser, initalize
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


def random_key(dictionary):
    return random.choice(list(dictionary.keys()))

async def choose_next_seed(SeedQ:dict, FailureQ:dict, type):
    """
    The function `choose_next_seed` selects a path or attribute along with a seed based on the type
    specified, and handles failures by updating dictionaries `SeedQ` and `FailureQ`.
    
    :param SeedQ: SeedQ is a dictionary containing information about seeds for different paths or
    attributes. It includes the methods and seeds associated with each path or attribute
    :type SeedQ: dict
    :param FailureQ: FailureQ is a dictionary that keeps track of failed requests for different paths or
    attributes. It stores information about failures for each path or attribute, including the methods
    that failed for each path and the seeds that were used for each attribute
    :type FailureQ: dict
    :param type: The `type` parameter in the `choose_next_seed` function represents the type of protocol
    being used, which can be either "http" or "coap"
    :return: The function `choose_next_seed` returns different values based on the input type. If the
    type is "http" or "coap", it returns a tuple containing the path and seed values. If the type is not
    "http" or "coap", it returns a tuple containing the seed, attribute, and object values.
    """
    if type == "http" or type == "coap":
        path = random_key(SeedQ)
        if SeedQ[path]["methods"] == {}:
            SeedQ.pop(path)
            return None, None

        if path not in FailureQ:
            FailureQ[path] = {}
            for method in SeedQ[path]["methods"]:
                FailureQ[path][method] = {}
        if len(SeedQ[path]["seeds"]) <= 0:
            seed = {"string": "sample"}
        else:
            seed = random.choice(SeedQ[path]["seeds"])
        return path, seed

    else:
        attribute = random_key(SeedQ)
        if attribute not in FailureQ:
            FailureQ[attribute] = []
        return random.choice(SeedQ[attribute]["seeds"]), attribute, SeedQ[attribute]["object"]


async def mutate_openapi(original_input, schema: Object):
    """
    The function `mutate_openapi` takes an original input and a schema object, and mutates the input
    based on the schema properties.
    
    :param original_input: The `original_input` parameter in the `mutate_openapi` function is expected
    to be a dictionary containing the input data that you want to mutate based on the provided schema.
    This input data will be modified according to the rules defined in the schema object
    :param schema: The `schema` parameter in the `mutate_openapi` function is expected to be an object
    that defines the structure of the input data. The function then mutates the original input data
    based on the schema provided. The schema can specify the type of each property in the input data,
    such as
    :type schema: Object
    :return: The function `mutate_openapi` returns the mutated input based on the provided schema. The
    mutated input is a dictionary containing the original input data with some mutations applied
    according to the schema properties. If the schema is a string, an empty string is returned. If the
    schema type is "object", the function iterates over the original input and applies mutations based
    on the schema properties. If the schema
    """
    muatated_input = dict()
    if type(schema) == str:
        return ""
    elif schema.type.value == "object":
        for x in original_input:
            i: Property
            for i in schema.properties:
                if x == i.name:
                    muatated_input[x] = copy.deepcopy(original_input[x])

                    if i.schema.type == "integer":
                        muatated_input[x] = mutation.random_mutation(
                            int(muatated_input[x])
                        )
                        # muatated_input[x] = int(muatated_input[x])
                    else:
                        muatated_input[x] = mutation.random_mutation(
                            str(muatated_input[x])
                        )
                        
                        # muatated_input[x] = str(muatated_input[x])
                    break
    elif schema.type.value == "string":
        muatated_input = copy.deepcopy(original_input)
        muatated_input = mutation.random_mutation(muatated_input["string"])
    return muatated_input


async def add_to_SeedQ(SeedQ, path, mutated_input_seed, type):
    """
    The function `add_to_SeedQ` appends mutated input seeds to a specified path in a SeedQ dictionary
    based on the type provided.
    
    :param SeedQ: SeedQ is a dictionary that contains information about different paths and their
    corresponding seeds. Each path in SeedQ is a key that maps to a dictionary containing a list of
    seeds
    :param path: The `path` parameter in the `add_to_SeedQ` function is used to specify the location
    within the `SeedQ` dictionary where the mutated input seed should be added
    :param mutated_input_seed: It seems like you missed providing the details of the
    `mutated_input_seed` parameter. Could you please provide more information about it so that I can
    assist you further with the `add_to_SeedQ` function?
    :param type: The `type` parameter in the `add_to_SeedQ` function is used to determine how the
    `mutated_input_seed` should be added to the `SeedQ`. Depending on the value of `type`, the function
    will append the `mutated_input_seed` in a specific format to
    """
    if type == "ble":
        SeedQ[path]["seeds"].append(mutated_input_seed["bytes"])
    elif type == "coap":
        SeedQ[path]["seeds"].append({"string":mutated_input_seed})
    else:
        SeedQ[path]["seeds"].append(mutated_input_seed)

async def seed_and_mutate_ble(SeedQ: dict):
    attribute = random_key(SeedQ)
    return random.choice(SeedQ[attribute]["value"]), None, SeedQ[attribute]["object"]
    




async def main():
    SeedQ, FailureQ, client, no_coverage, total_coverage_data, interesting_time, failure_time, tests, args = await initalize()
    start_time = time.time()
    try:
        server_process = await client.call_process("main_program")
        await asyncio.sleep(2)
    except Exception as e:
        print(e + " " + "Not able to run server, please set --no-coverage")
        raise e
    try:
        await asyncio.sleep(5)
        while SeedQ:
            # AssignEnergy
            if args.arg1 == "coap" or args.arg1 == "http":
                if args.arg1 == "http":
                    await client.login("example", "example")
                path, seed = await choose_next_seed(SeedQ, FailureQ, args.arg1)
                if path == None:
                    continue
            elif args.arg1 == "ble":
                # TODO choose next service/charactistics to fuzz
                seed, path, method = await choose_next_seed(SeedQ, FailureQ, args.arg1)
                seed = {"bytes": seed}
            energy = assign_energy.AssignEnergy(seed)
            for _ in range(energy):
                # For Django and Coap
                if args.arg1 == "coap" or args.arg1 == "http":
                    mutated_input_seed = await mutate_openapi(seed, SeedQ[path]["schema"])
                    add = False
                    for method in SeedQ[path]["methods"]:
                        response_payload, status_code = await client.send_payload(
                            mutated_input_seed, path, method, SeedQ[path]["schema"]
                        )
                        
                        tests[len(tests)] = datetime.now().isoformat()
                        await asyncio.sleep(0.2)
                        # Check if the process has terminated
                        if no_coverage == False:
                            if server_process.poll() is not None:
                                print("Server crashed/timeout! Adding to the FailureQ.")
                                if status_code not in FailureQ[path]:
                                    FailureQ[path][method] = dict()
                                if status_code not in FailureQ[path][method]:
                                    FailureQ[path][method][status_code] = []
                                FailureQ[path][method][status_code].append(
                                    (mutated_input_seed, response_payload)
                                )
                                if len(FailureQ[path][method][status_code]) == 1:
                                    failure_time[len(failure_time.keys())] = datetime.now().isoformat()
                                server_process.terminate()
                                server_process = await client.call_process("main_program")
                                print("Server Restarting!")
                                await asyncio.sleep(2)

                        current_coverage_data = await get_coverage_data(args.arg1)
                        if await is_interesting(
                                total_coverage_data,
                                current_coverage_data,
                                interesting_time,
                                mutated_input_seed,
                                f'{path}:{method}'
                            ):
                                add = True
                                # Add to SeedQ
                        
                    if add == True:
                        await add_to_SeedQ(SeedQ, path, mutated_input_seed, args.arg1)



                elif args.arg1 == "ble":
                    mutated_input_seed = dict()
                    tests[len(tests.keys())] = datetime.now().isoformat()
                    mutated_input_seed["bytes"] = mutation.random_mutation(seed["bytes"])
                    if isinstance(mutated_input_seed["bytes"] , int):
                        mutated_input_seed["bytes"]  = bytes([mutated_input_seed["bytes"] ])
                    elif isinstance(mutated_input_seed["bytes"] , str):
                        mutated_input_seed["bytes"]  = mutated_input_seed["bytes"].encode("utf-8")
                    driver = client.send_payload(mutated_input_seed, path, method)
                    server_process = await client.call_process()
                    response_payload, status_code = await driver
                    if no_coverage == False:
                        if server_process.poll() is not None:
                            print("Server crashed/timeout! Adding to the FailureQ.")
                            if status_code not in FailureQ[method]:
                                FailureQ[method][status_code] = []
                            FailureQ[method][status_code].append(
                                (mutated_input_seed["bytes"].hex(), response_payload)
                            )
                            if len(FailureQ[method][status_code]) == 1:
                                failure_time[len(failure_time.keys())] = datetime.now().isoformat()
                    server_process.terminate()
                    await asyncio.sleep(0.25)
                    current_coverage_data = await get_coverage_data(args.arg1)
                    if await is_interesting(
                            total_coverage_data,
                            current_coverage_data, 
                            interesting_time,
                            mutated_input_seed,
                            method
                        ):
                            # Add to SeedQ
                            await add_to_SeedQ(SeedQ, path, mutated_input_seed, args.arg1)
                
                os.system('cls' if os.name=='nt' else 'clear')
                print("Finished sending mutated input:")
                print(mutated_input_seed)
                print("At: ")
                print(path)
                print(method)
                print()
                print("No of Interesting Test Cases: " + str(len(interesting_time.keys()) - 1))
                print("No of Failures: " + str(len(failure_time.keys()) - 1))
                print("No of tests: " + str(len(tests.keys()) - 1))
                current_runtime = time.time() - start_time
                print(f"Current running time: {current_runtime:.2f} secs")


    except KeyboardInterrupt as e:
        print(e)

    except Exception as e:
        print(f"{traceback.format_exc()}")

    finally:
        try:
            print("\nShutting Down Server! please wait...")
            server_process.send_signal(signal.SIGINT)
            # subprocess.run(["sudo", "fuser", "-k", "8000/tcp"])
            # subprocess.run(["sudo", "fuser", "-k", "9000/tcp"])
            # subprocess.run(["sudo", "fuser", "-k", "5683/tcp"])
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
        if args.arg1 == "coap" or args.arg1 == "http":
            for path in SeedQ:
                SeedQ[path].pop("schema")
        else:
            for attribute in SeedQ:
                SeedQ[attribute].pop("object")
                new_list = list()
                for x in SeedQ[attribute]["seeds"]:
                    try:
                        new_list.append(x.hex())
                    except:
                        new_list.append(x.encode('utf-8').hex())
                SeedQ[attribute]["seeds"] = new_list
            for x in interesting_time:
                if x != 0:
                    if type(interesting_time[x]) != str:
                        try:
                            interesting_time[x]["input"]["bytes"] = interesting_time[x]["input"]["bytes"].hex()
                        except:
                            interesting_time[x]["input"]["bytes"] = interesting_time[x]["input"]["bytes"].encode('utf-8').hex()
        with open("SeedQ.json", "w") as json_file:
            json.dump(SeedQ, json_file)
        with open("FailureQ.json", "w") as json_file:
            json.dump(FailureQ, json_file)
        with open("interesting.json", "w") as json_file:
            json.dump(interesting_time, json_file)
        with open("failure.json", "w") as json_file:
            json.dump(failure_time, json_file)
        with open("tests.json", "w") as json_file:
            json.dump(tests, json_file)
        return


if __name__ == "__main__":
    asyncio.run(main())
    # file = asyncio.run(get_latest_file("./coverages"))
    # os.remove(file)
    args = asyncio.run(init_parser())
    if args.python2 == True and (args.arg1 == "http" or args.arg1 == "coap"):
        subprocess.run(["python2", "-m", "coverage", "combine", "--rcfile=./.coveragerc", "-a"])
        subprocess.run(["python2", "-m", "coverage", "report"])
    elif args.arg1 == "http" or args.arg1 == "coap":
        subprocess.run(["coverage", "combine", "--rcfile=./.coveragerc", "-a"])
        subprocess.run(["coverage", "report"])

    print("removing htmlcov...")
    try:
        shutil.rmtree("./htmlcov")
        shutil.rmtree("./lcov_html")
    except:
        pass
    print("generating htmlcov...")
    subprocess.run(["coverage", "html"])
    subprocess.run(["genhtml", "lcov.info", "--output-directory", "lcov_html", "-q", "--ignore-errors", "source", "--highlight", "--legend"],stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL)

