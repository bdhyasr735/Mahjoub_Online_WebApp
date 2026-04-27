import requests
import os

# جلب المفاتيح السيادية من متغيرات البيئة (Railway)
QUMRA_API_URL = os.getenv("QUMRA_API_URL")  # الرابط المباشر لـ GraphQL
QUMRA_TOKEN = os.getenv("QUMRA_API_KEY")    # التوكن qmr_...

def query_qumra(query, variables=None):
    """المحرك الأساسي لإرسال استعلامات GraphQL إلى قمرة"""
    if not QUMRA_API_URL or not QUMRA_TOKEN:
        print("🔴 خطأ: مفاتيح QUMRA غير معرفة في متغيرات البيئة.")
        return None

    headers = {
        "Authorization": f"Bearer {QUMRA_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"query": query, "variables": variables}
    
    try:
        response = requests.post(QUMRA_API_URL, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"🔴 فشل الاتصال بقمرة: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"🔴 خطأ تقني في المحرك: {e}")
        return None

def fetch_qumra_collections():
    """جلب الأقسام من قمرة لتظهر للمورد كقائمة اختيار جاهزة"""
    query = """
    query {
      collections(first: 50) {
        edges {
          node {
            id
            name
          }
        }
      }
    }
    """
    result = query_qumra(query)
    if result and 'data' in result and result['data'].get('collections'):
        return [
            (edge['node']['id'], edge['node']['name']) 
            for edge in result['data']['collections']['edges']
        ]
    return []

def create_qumra_product(name, description, price, collection_id, image_urls=None):
    """إرسال المنتج نهائياً إلى قمرة (النشر السيادي)"""
    mutation = """
    mutation CreateProduct($input: ProductInput!) {
      productCreate(input: $input) {
        product {
          id
          name
        }
        userErrors {
          field
          message
        }
      }
    }
    """
    
    variables = {
        "input": {
            "name": name,
            "descriptionHtml": description,
            "collections": [collection_id] if collection_id else [],
            "variants": [
                {
                    "price": float(price),
                    "inventoryQuantity": 10
                }
            ]
        }
    }
    
    if image_urls:
        variables["input"]["images"] = [{"src": url} for url in image_urls]

    return query_qumra(mutation, variables)
