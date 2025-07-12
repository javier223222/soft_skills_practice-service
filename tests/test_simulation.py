import requests
import json

url = "http://localhost:8000/simulation/start"
headers = {"Content-Type": "application/json"}
data = {
    "user_id": "user123",
    "scenario_id": "68671d8ee0fb8100716b7ff2"
}

try:
    response = requests.post(url, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
