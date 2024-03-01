import argparse
import asyncio
import json
import random

from coap.input import COAPClient
from django.input import DjangoClient
import assign_energy
from mutations import mutation
from openapi_parser import parse
from openapi_parser.specification import Path, Object

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
    if any(indicator in response_payload.lower() for indicator in sensitive_info_indicators):
        print("Found potential sensitive information in the response.")
        return True

    return False

def choose_next(SeedQ):
    return random.choice(SeedQ)


async def main():
    try:
        FailureQ = {}
        parser = argparse.ArgumentParser(description='Description of your script')
        parser.add_argument('arg1', type=str, help='Protocol of Request')
        parser.add_argument('arg2', type=str, help='OpenAPI 3.03 json file')
        
        args = parser.parse_args()

        try:
            grammar = parse(args.arg2)
        
        except Exception as e:
            print(e)
            return
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
            
        # load all examples/inputs into SeedQ
        # select random path and method in grammar
        SeedQ = dict()
        for path in grammar.paths:
            methods = path.operations
            SeedQ[path.url] = dict()
            for operation in methods:
                method = operation.method.value
                body = operation.request_body
                if body != None:
                    if body.content[0].schema.type.value == "string":
                        SeedQ[path.url][method] = {"string": body.content[0].schema.example}
                    elif body.content[0].schema.type.value == "object":
                        object: Object = body.content[0].schema
                        SeedQ[path.url][method] = {}
                        for i in object.properties:
                            SeedQ[path.url][method][i.name] = i.schema.example
        
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
                #TODO mutate input
                payload = SeedQ[path][method]
                for x in payload:
                    print(x)
                    payload[x] = mutation.random_byte(payload[x])
                
                response_payload, status_code = await client.send_payload(payload, path, method)
                print(f"Path: {path}")
                print(f"Payload: {payload}")
                print(f"Response: {response_payload}")
                print(f"Status code: {status_code}\n")

                #TODO isInteresting
                if is_interesting(response_payload, status_code):
                    print("Interesting finding! Adding to the FailureQ.")
                    if status_code not in FailureQ[path][method]:
                        FailureQ[path][method][status_code] = []
                    FailureQ[path][method][status_code].append((payload, response_payload))
    
    except KeyboardInterrupt:
        pass
    
    except Exception as e:
        print(f"An error occurred: {e}")
        raise e
    finally:
        log = ""
        print()
        #print("FailureQ: ", FailureQ)
        for x in FailureQ:
            #print(x)
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