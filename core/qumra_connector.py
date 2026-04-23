import requests
from flask import current_app

class QumraEngine:
    """محرك الربط مع منصة قمرة عبر GraphQL"""
    
    @staticmethod
    def get_headers():
        """تجهيز ترويسة المصادقة باستخدام مفتاحك"""
        return {
            "Authorization": f"Bearer {current_app.config['QUMRA_API_KEY']}",
            "Content-Type": "application/json"
        }

    @classmethod
    def fetch_products(cls):
        """سحب قائمة المنتجات من قمرة لمراجعتها"""
        query = """
        query {
          findAllProducts {
            id
            name
            price
            images {
              url
            }
          }
        }
        """
        try:
            response = requests.post(
                current_app.config['QUMRA_API_URL'],
                json={'query': query},
                headers=cls.get_headers(),
                timeout=10 # رشيقة: لا تنتظر أكثر من 10 ثوانٍ
            )
            if response.status_code == 200:
                return response.json().get('data', {}).get('findAllProducts', [])
            return []
        except Exception as e:
            print(f"Error fetching from Qumra: {e}")
            return []

    @classmethod
    def sync_order_status(cls, qumra_order_id, status):
        """تحديث حالة الطلب في قمرة (مثل: تم التجهيز)"""
        mutation = """
        mutation($id: ID!, $status: String!) {
          updateOrderStatus(id: $id, status: $status) {
            id
            status
          }
        }
        """
        variables = {"id": qumra_order_id, "status": status}
        response = requests.post(
            current_app.config['QUMRA_API_URL'],
            json={'query': mutation, 'variables': variables},
            headers=cls.get_headers()
        )
        return response.status_code == 200
