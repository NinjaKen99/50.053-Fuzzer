import argparse
import asyncio
import json
import random

from coap.input import COAPClient
from django.input import DjangoClient
import assign_energy


def random_key(dictionary):
    return random.choice(list(dictionary.keys()))

def is_interesting(response_payload, status_code):
    """Check if the response indicates a potential error or contains sensitive information."""
    # Check if the status code indicates a server error
    if status_code >= 500:
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
    if any(indicator in response_payload.lower() for indicator in sensitive_info_indicators):
        print("Found potential sensitive information in the response.")
        return True

    return False

async def main():
    parser = argparse.ArgumentParser(description='Description of your script')
    parser.add_argument('arg1', type=str, help='Protocol of Request')
    parser.add_argument('arg2', type=str, help='Url paths in Openapi json format')
    parser.add_argument('arg3', type=str, help='inital seeds for the fuzzing in json format')
    
    args = parser.parse_args()

    with open(args.arg2) as f:
        # Load the JSON data
        grammar = json.load(f)
    
    with open(args.arg3) as f:
        # Load the JSON data
        dictionary = json.load(f)
    

    url = grammar["servers"][0]["url"]
    match args.arg1:
        
        case "coap":
            client = COAPClient(url)
        
        case "http":
            client = DjangoClient(url)
        
        case _:
            raise ValueError("Invalid protocol") 

    # select random path and method in grammar
    path = random_key(grammar["paths"])
    methods = grammar["paths"][path]
    method = random_key(methods)

    # Initialize your seed and failure queues
    SeedQ = dictionary
    FailureQ = []

    while SeedQ:
        # TODO ChooseNext from SeedQ
        seed = ''

        # AssignEnergy
        energy = assign_energy.AssignEnergy(seed)

        for _ in range(energy):
            #TODO mutate input
            payload = ''

            response_payload, status_code = await client.send_payload(payload, path, method)
            print(f"Path: {path}")
            print(f"Payload: f{payload}")
            print(f"Response: {response_payload}")
            print(f"Status code: f{status_code}\n")

            #TODO isInteresting
            if is_interesting(response_payload, status_code):
                print("Interesting finding! Adding to the FailureQ.")
                FailureQ.append((payload, response_payload, status_code))

    # TODO: Save files in something

    
    
        
        
    
    
    '''
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
    '''

if __name__ == "__main__":
    asyncio.run(main())