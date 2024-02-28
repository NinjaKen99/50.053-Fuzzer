from aiocoap import Message, Context
from aiocoap import Code
import random
import string
import asyncio



class COAPClient:
    def __init__(self, url):
        self.url = url
    
    async def code_to_str(self, code: Code):
        string =  code.__str__()[0:4]
        return string.replace(".", "")
        
    
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
    

    async def send_payload(self, payload, uri, code):
        protocol = await Context.create_client_context()
        code = await self.str_to_code(code)
        print(f"Sending payload: {payload} to {self.url}{uri} with {code}")
        # await asyncio.sleep(random.uniform(0, 1))  # Simulate network delay
        msg = Message(code=code, uri=f"{self.url}{uri}", payload=bytes(payload, "utf-8"))
        response: Message = await protocol.request(msg).response
        return response.payload.decode(), await self.code_to_str(response.code)
    

# async def main():
#     client = COAPClient("coap://127.0.0.1:5683")
#     s = await client.send_payload("Hellfsfsfo World!", "/child", "get")
#     print(s)
    

# asyncio.run(main())