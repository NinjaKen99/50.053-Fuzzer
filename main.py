import argparse
import asyncio
import json
import random

from coap.input import COAPClient
from django.input import DjangoClient
import assign_energy
from mutations import mutation


def random_key(dictionary):
    return random.choice(list(dictionary.keys()))

def is_interesting(response_payload, status_code):
    """Check if the response indicates a potential error or contains sensitive information."""
    # Check if the status code indicates a server error
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
    if any(indicator in response_payload.lower() for indicator in sensitive_info_indicators):
        print("Found potential sensitive information in the response.")
        return True

    return False

def choose_next(SeedQ):
    return random.choice(SeedQ)


async def main():
    try:
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
        SeedQ = dictionary["paths"]
        
        FailureQ = {}

        while SeedQ:
            # TODO ChooseNext from SeedQ
            key = random_key(SeedQ)
            key2 = random_key(SeedQ[key])
            seed = SeedQ[key][key2]

            if key not in FailureQ:
                FailureQ[key] = {}
            if key2 not in FailureQ[key]:
                FailureQ[key][key2] = {}
            # AssignEnergy
            energy = assign_energy.AssignEnergy(seed)
            for _ in range(energy):
                #TODO mutate input
                payload = seed["input"]

                payload = mutation.random_byte(payload)
                response_payload, status_code = await client.send_payload(payload, path, key2)
                print(f"Path: {path}")
                print(f"Payload: {payload}")
                print(f"Response: {response_payload}")
                print(f"Status code: {status_code}\n")

                #TODO isInteresting
                if is_interesting(response_payload, int(status_code)):
                    print("Interesting finding! Adding to the FailureQ.")
                    if status_code not in FailureQ[key][key2]:
                        FailureQ[key][key2][status_code] = []
                    FailureQ[key][key2][status_code].append((payload, response_payload))
    
    except Exception as e:
        print(e)     
    except KeyboardInterrupt:
        pass
    

    finally:
        log = ""
        print()
        print("FailureQ: ", FailureQ)
        for x in FailureQ:
            print(x)
            log+= x + ":\n"
            for y in FailureQ[x]:
                for z in FailureQ[x][y]:
                    print(f"code:{y}, status code: {z}, no = {len(FailureQ[x][y][z])}")
                    log+= f"code:{y}, status code: {z}, no = {len(FailureQ[x][y][z])}\n"
        
        with open("log.json", 'w') as json_file:
            json.dump(FailureQ, json_file)
        with open("log.txt", 'w') as file:
            file.write(log)
        await asyncio.sleep(20)
        print("Exiting...")
        await asyncio.sleep(5)
    
        
        
    
    
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