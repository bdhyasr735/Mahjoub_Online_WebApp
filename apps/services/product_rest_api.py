import requests
import os

api_key = os.environ.get('QUMRA_API_KEY')
url = "https://mahjoub.online/api/products"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "title": "منتج تجريبي من REST",
    "price": 99.99,
    "quantity": 5,
    "status": "DRAFT",
    "images": []
}

response = requests.post(url, json=payload, headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
