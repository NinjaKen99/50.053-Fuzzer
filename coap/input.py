from aiocoap import Message, Context
from aiocoap import Code
import random
import string



class COAPClient:
    def __init__(self):
        self.host = "localhost"
        self.port = "5683"
        self.uri = {
            "basic": [Code.GET, Code.PUT, Code.POST, Code.DELETE], 
            "storage": [Code.GET, Code.POST], 
            "child": [Code.GET, Code.PUT, Code.POST, Code.DELETE],
            "seperate": [Code.GET], 
            "long": [Code.GET],
            "big": [Code.GET, Code.POST],
            "void": [],
            "xml": [Code.GET],
            "encoding": [Code.GET, Code.PUT, Code.POST],
            "etag": [Code.GET, Code.PUT, Code.POST],
            "advanced": [Code.GET, Code.PUT, Code.POST, Code.DELETE],
            "advancedSeperate": [Code.GET, Code.PUT, Code.POST, Code.DELETE]
        }
    
    async def code_to_str(self, code: Code):
        return code.__str__()
    
    async def get_codes(self, uri):
        return self.uri.get(uri, None)
    
    async def get_uris(self):
        return dict.keys(self.uri)

    async def send_payload(self, payload, uri):
        protocol = await Context.create_client_context()
        msg = Message(code=Code.GET, uri=f"coap://{self.host}:{self.port}/{uri}", payload=payload)
        response: Message = await protocol.request(msg).response
        
        return {response.payload, self.code_to_str(response.code)}