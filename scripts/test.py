import os
import json
import requests

USERNAME = os.getenv("USER", None)
API_TOKEN = os.getenv("API_TOKEN", None)

response = requests.get('https://api.github.com/user', auth=(USERNAME, API_TOKEN))
print(json.dumps(response.json(), indent=2, sort_keys=True))
