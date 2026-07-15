# 📂 apps/services/graphql_client.py
import requests
import os

class QomrahGraphQLClient:
    @staticmethod
    def fetch_orders(headers=None):
        api_key = os.environ.get('QUMRA_API_KEY')
        url = "https://api.qomrah.com/graphql"
        
        # استعلام لجلب الطلبات (كما يتوقع sync_engine)
        query = """
        query {
          findAllOrders {
            _id
            customerName
            totalPrice
            tracking_tag
            items {
              productName
              quantity
              price
              sku
            }
          }
        }
        """
        
        # دمج الترويسات المرسلة من sync_engine مع المصادقة
        default_headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        if headers:
            default_headers.update(headers)
            
        response = requests.post(url, json={'query': query}, headers=default_headers)
        
        if response.status_code == 200:
            return response.json().get('data', {}).get('findAllOrders', [])
        else:
            raise Exception(f"فشل الاتصال بـ قمرة: {response.status_code}")
