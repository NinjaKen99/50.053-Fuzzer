import os
import subprocess
from aiocoap import Message, Context
from aiocoap import Code
import random
import string
import asyncio


class COAPClient:
    def __init__(self, url, directory, command:str):
        self.url = url
        self.directory = directory
        self.command = command

    async def code_to_str(self, code: Code):
        string = code.__str__()[0:4]
        return string.replace(".", "")

    async def call_process(self, context):
        command_list = ["python2","-m", "coverage", "run", "--rcfile=../../.coveragerc", f"--context={context}"] + self.command.split()
        return subprocess.Popen(command_list,
            cwd=self.directory,
            preexec_fn=os.setpgrp,
        )

    async def str_to_code(self, code: str):
        match code:
            case "get":
                return Code.GET

            case "post":
                return Code.POST

            case "put":
                return Code.PUT

            case "delete":
                return Code.DELETE
            case _:
                raise ValueError(f"Unknown code: {code}")

    async def send_payload(self, payload, uri, code, schema):
        try:

            protocol = await Context.create_client_context()
            code = await self.str_to_code(code)
            # print(f"Sending payload: {payload} to {self.url}{uri} with {code}")
            msg = Message(
                code=code, uri=f"{self.url}{uri}", payload=bytes(payload, "utf-8")
            )
            try:
                response: Message = await asyncio.wait_for(protocol.request(msg).response, 60)
                return response.payload.decode(), await self.code_to_str(response.code)
            except asyncio.TimeoutError:
                print("Request timed out.")
            finally:
                await protocol.shutdown()
            # Extract coverage data from the response
            # if response.status_code == 200:
            #     data = response.json()
            #     coverage_data = data.get('coverage', {})
                # Return coverage data along with other response details
            return None, None
        except Exception as e:
            print("Something happened!")
            print(e)
            return None, None

        


# async def main():
#     client = COAPClient("coap://127.0.0.1:5683", "", "")
#     print(await client.send_payload("New payloa\u001b_\u0019\u0010r PUT", "/advanced", "get", ""))


# asyncio.run(main())
