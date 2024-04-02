import os
import re
import subprocess
import requests
import httpx





class DjangoClient:

    def __init__(self, url):
        self.url = url
        self.client = httpx.AsyncClient(timeout=30)

    
    async def call_process(self, context):
        return subprocess.Popen(
                    [
                        "coverage",
                        "run",
                        "--rcfile=../../.coveragerc",
                        f"--context={context}",
                        "manage.py",
                        "runserver",
                        "8000",
                        "--noreload",
                    ],
                    cwd="./targets/DjangoWebApplication",
                    preexec_fn=os.setpgrp,
                )
    async def send_payload(self, input, uri, code):
        # Replace 'http://<Django app URL>' with the base URL of your Django app (e.g., 'http://localhost:8000')

        registration_endpoint = f'{uri}'

        registration_url = self.url + registration_endpoint
        pattern = r'\{.*?\}'
        matches = re.findall(pattern, registration_url)
        
        if matches:
            for x in matches:
                if x[1:-1] in input:
                    print(x[1:-1])
                    print(input[x[1:-1]])
                    registration_url = registration_url.replace(x, input[x[1:-1]])
        try:
            match code:
                case "get":
                    response =  await self.client.get(registration_url, follow_redirects=True)
                case "post":
                    # Send a POST request to the registration endpoint with the user data
                    response =  await self.client.post(registration_url, json=input,  follow_redirects=True)
                case "put":
                    response =  await self.client.put(registration_url, json=input,  follow_redirects=True)
                case "delete":
                    response =  await self.client.delete(registration_url,  follow_redirects=True)

            # Extract coverage data from the response
            print(response)
            if response.status_code == 200:
                data = response.json()
                print(data)
                coverage_data = data.get('coverage', {})
                # Return coverage data along with other response details
                return response.reason_phrase, response.status_code
            else:
                return response.reason_phrase, response.status_code
                
        except requests.exceptions.RequestException as e:
            print("User registration request failed:", e)
            return None, None

        except Exception as e:
            return None, None
