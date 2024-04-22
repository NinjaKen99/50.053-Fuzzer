
import argparse
from datetime import datetime
import json
import os
import subprocess

from coap.input import COAPClient
from django.input import DjangoClient
from openapi_parser import parse
from openapiparser import parse_new_openapi
from coverages import *
from zephyr.input import BLEClient
import subprocess


async def init_parser():
    parser = argparse.ArgumentParser(description="Description of your script")
    parser.add_argument("arg1", type=str, help="Protocol of Request")
    parser.add_argument(
        "--file", type=str, help="OpenAPI 3.03 json file", required=False
    )
    parser.add_argument(
        "--nocoverage", action="store_true", help="Disable code coverage"
    )
    parser.add_argument("--restart", action="store_true", help="Continue off from last fuzzing session")
    parser.add_argument("--python2", action="store_true", help="run commands as python2")
    parser.add_argument('directory', type=str, help='Where the application is')
    parser.add_argument('command', type=str, help='Specify the command to run (e.g., "manage.py runserver 8000 --noreload")')
    args = parser.parse_args()
    return args


async def initalize():
    """
    The function initializes different clients based on the specified protocol, loads existing data if
    restart is False, and handles coverage data and file operations.
    """
    args = await init_parser()
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
    # Specify the directory where you want to delete files
    directory = "./coverages"

    # List all files in the directory
    files = os.listdir(directory)

    # Filter files that start with ".coverage"
    coverage_files = [file for file in files if file.startswith(".coverage")]
    # coverage_files.remove(".coverage")
    # Delete each file
    interesting_time = {0:datetime.now().isoformat()}
    failure_time = {0:datetime.now().isoformat()}
    tests = {0:datetime.now().isoformat()}
    FailureQ = {}
    match args.arg1:

        case "coap":
            client = COAPClient(url.url, args.directory, args.command)
            SeedQ = parse_new_openapi(grammar)

        case "http":
            client = DjangoClient(url.url, args.directory, args.command)
            SeedQ = parse_new_openapi(grammar)

        case "ble":
            client = BLEClient(9000, args.directory, args.command)
            await client.initalize_transport()
            SeedQ = await client.get_services()          

        case _:
            raise ValueError("Invalid protocol")
        
    if args.restart == False:
        with open('SeedQ.json', "r") as f:
            existing_SeedQ = json.load(f)
        for x in existing_SeedQ:
            if args.arg1 == "ble":
                new_list = list()
                for y in existing_SeedQ[x]["seeds"]:
                    try:
                        new_list.append(bytes.fromhex(y).decode('utf-8'))
                    except UnicodeDecodeError as e:
                        new_list.append(bytes.fromhex(y))
                existing_SeedQ[x]["seeds"] = new_list
            SeedQ[x]["seeds"] = existing_SeedQ[x]["seeds"]

        with open("FailureQ.json", "r") as g:
            FailureQ = json.load(g)
        if os.path.isfile("./interesting.json") == True:
            with open("interesting.json", "r") as f:
                interesting_time = json.load(f)
        else:
            interesting_time = {0:datetime.now().isoformat()}
    
        if os.path.isfile("./failure.json") == True:
            with open("failure.json", "r") as f:
                failure_time = json.load(f)
        else:
            failure_time = {0:datetime.now().isoformat()}
        if os.path.isfile("./tests.json") == True:
            with open("tests.json", "r") as f:
                tests = json.load(f)
        else:
            tests = {0:datetime.now().isoformat()}
        total_coverage_data = await get_coverage_data(args.arg1)
    else:
        total_coverage_data = dict()
        if args.arg1 == "coap" or args.arg1 == "http":
            for file in coverage_files:
                file_path = os.path.join(directory, file)
                os.remove(file_path)
        #remove lcov info
        else:
            try:    
                subprocess.run(["lcov", "--zerocounters", "-d", "./targets/Zephyr"])
            except:
                pass
            try:
                os.remove("lcov.info")
            except:
                pass
    no_coverage = args.nocoverage
    # load all examples/inputs into SeedQ
    # select random path and method in grammar

    return SeedQ, FailureQ, client, no_coverage, total_coverage_data, interesting_time, failure_time, tests, args