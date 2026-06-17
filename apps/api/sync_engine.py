import requests
from apps.models.orders_db import ProcessedOrder, db
import logging

class SyncEngine:
    API_URL = "https://mahjoub.online/admin/graphql" # كما هو في الـ Endpoint الخاص بك
    API_TOKEN = "qmr_e063f7f4-ed44-4c86-b105-8405326b9eb9"

    @staticmethod
    def fetch_and_sync_order(order_id=None):
        """جلب الطلبات من GraphQL وتخزينها محلياً"""
        
        # استعلام GraphQL لجلب بيانات الطلب (عدل الحقول حسب الـ Schema لديك)
        query = """
        query {
            orders {
                id
                status
                totalPrice
                createdAt
                customerName
            }
        }
        """
        
        headers = {
            "Authorization": f"Bearer {SyncEngine.API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(SyncEngine.API_URL, json={'query': query}, headers=headers)
            result = response.json()
            
            orders_data = result.get('data', {}).get('orders', [])
            
            for item in orders_data:
                # التحقق هل الطلب موجود مسبقاً؟
                order = ProcessedOrder.query.get(item['id'])
                if not order:
                    new_order = ProcessedOrder(
                        id=item['id'],
                        status=item['status'],
                        total_price=float(item['totalPrice']),
                        customer_name=item['customerName']
                    )
                    db.session.add(new_order)
            
            db.session.commit()
            return True
        except Exception as e:
            logging.error(f"❌ Sync Error: {e}")
            return False
