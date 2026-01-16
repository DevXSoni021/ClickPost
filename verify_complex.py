import requests
import json

url = "http://localhost:8000/query"
payload = {
    "query": "I am worried about my 4K Ultra HD Gaming Monitor. Can you find the order, track the shipment, and check my support tickets?",
    "user_id": 1
}

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print("Response JSON:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
