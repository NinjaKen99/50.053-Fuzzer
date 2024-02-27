from aiocoap import Message, Context
from aiocoap import Code
import random
import string



class COAPClient:
    def __init__(self, url):
        self.url = url
    
    async def code_to_str(self, code: Code):
        return code.__str__()
    
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
        msg = Message(code=(await self.str_to_code(code)), uri=f"url{uri}", payload=payload)
        response: Message = await protocol.request(msg).response
        return response.payload, self.code_to_str(response.code)