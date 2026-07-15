# 📂 apps/services/graphql_client.py (قم بإنشاء هذا الملف)
import requests
import os

def fetch_products_from_qomrah():
    api_key = os.environ.get('QUMRA_API_KEY')
    url = "https://api.qomrah.com/graphql" # أو رابط الـ API الخاص بمتجرك
    
    query = """
    query {
      findAllProducts {
        _id
        title
        sku
        price
        quantity
      }
    }
    """
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json={'query': query}, headers=headers)
    if response.status_code == 200:
        return response.json().get('data', {}).get('findAllProducts', [])
    else:
        raise Exception(f"فشل الاتصال بقمرة: {response.status_code}")
