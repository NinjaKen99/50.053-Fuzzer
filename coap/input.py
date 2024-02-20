from aiocoap import Message, Context
from aiocoap import Code
import random
import string



async def send_payload(input):
    payload = "Hello, CoAP!"
    num_bytes = 5
    protocol = await Context.create_client_context()
    fuzz_bytes = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(num_bytes))
    payload = payload[:3] + fuzz_bytes + payload[3 + num_bytes:]
    msg = Message(code=Code.GET, uri="coap://localhost:5683/basic", payload=payload)
    response: Message = await protocol.request(msg).response
    print(response.payload)
    