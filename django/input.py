import requests
import httpx





class DajngoClient:

    def __init__(self):
        self.host = "localhost"
        self.port = 8000
        self.client = httpx.AsyncClient(http2=True)
        self.uri = {
            "api/product": ["GET", "POST", "PUT", "DELETE"],
            "login/jwt": ["POST"],
            "accounts/register":["POST"],
            "": ["GET"],
            "tables": ["GET"],
            "datab/product/add":["POST"]
        }

    
    
    async def get_codes(self, uri):
        return self.uri.get(uri, None)
    
    async def get_uris(self):
        return dict.keys(self.uri)
    
    async def send_payload(self, input, uri, code):
        # Replace 'http://<Django app URL>' with the base URL of your Django app (e.g., 'http://localhost:8000')
        base_url = f'http://{self.host}:{self.port}'

        registration_endpoint = f'/{uri}'

        registration_url = base_url + registration_endpoint

        user_data = {
            'username': 'john',
            'email': 'john@example.com',
            'password1': 'MyPassword123',
            'password2': 'MyPassword123'  # Confirm password
        }

        try:
            match uri:
                
                case "GET":
                    pass
                case "POST":
                    # Send a POST request to the registration endpoint with the user data
                    response =  await self.client.post(registration_url, json=user_data)
                    # Check if the request was successful (status code 200 or 201 for successful creation)
                    if response.status_code in (200, 201):
                        print("User registration successful!")
                        print("Response:")
                        print(response.text)
                    else:
                        print(f"User registration failed with status code: {response.status_code}")
                case "PUT":
                    pass
                case "DELETE":
                    pass

        except requests.exceptions.RequestException as e:
            print("User registration request failed:", e)
