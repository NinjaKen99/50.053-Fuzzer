import requests
import httpx





class DjangoClient:

    def __init__(self, url):
        self.url = url
        self.client = httpx.AsyncClient()

    
    async def send_payload(self, input, uri, code):
        # Replace 'http://<Django app URL>' with the base URL of your Django app (e.g., 'http://localhost:8000')

        registration_endpoint = f'{uri}'

        registration_url = self.url + registration_endpoint

        try:
            match code:
                case "get":
                    response =  await self.client.get(registration_url, json=input)
                case "post":
                    # Send a POST request to the registration endpoint with the user data
                    response =  await self.client.post(registration_url, json=input)
                case "put":
                    response =  await self.client.put(registration_url, json=input)
                case "delete":
                    response =  await self.client.delete(registration_url, json=input)
                
            return response.text, response.status_code
        except requests.exceptions.RequestException as e:
            print("User registration request failed:", e)
            return None, None
