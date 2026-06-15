# 📂 apps/utils/orders_engine.py
from apps.extensions import db
from apps.models.order_db import Order
import requests
import logging

logger = logging.getLogger(__name__)

class OrdersEngine:
    def __init__(self):
        self.api_url = "https://mahjoub.online/admin/graphql"
        self.api_key = "qmr_e063f7f4-ed44-4c86-b105-8405326b9eb9"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}", 
            "Content-Type": "application/json"
        }

    def fetch_orders_from_qumra(self):
        print("DEBUG: محاولة الاتصال بـ API قمرة...")
        payload = {
            "query": """
            query {
                findAllOrders(input: { limit: 50, page: 1 }) {
                    data {
                        _id
                        total
                        status
                        customer { name }
                    }
                }
            }
            """
        }
        try:
            response = requests.post(self.api_url, json=payload, headers=self.headers, timeout=15)
            result = response.json()
            
            # طباعة الرد الخام لكشف ما يحدث في الخلفية
            print(f"DEBUG: رد السيرفر الخام: {result}")
            
            # محاولة الاستخراج
            orders = result.get('data', {}).get('findAllOrders', {}).get('data', [])
            print(f"DEBUG: تم استخراج {len(orders)} طلب من البيانات.")
            return orders
        except Exception as e:
            print(f"DEBUG: حدث خطأ أثناء الاتصال: {str(e)}")
            return []

    def sync_orders_to_db(self):
        print("DEBUG: بدء عملية المزامنة...")
        orders = self.fetch_orders_from_qumra()
        
        count = 0
        for item in orders:
            order_id = str(item.get('_id'))
            if not order_id: continue
            
            order = Order.query.filter_by(order_id_qumra=order_id).first() or Order(order_id_qumra=order_id)
            
            order.total = float(item.get('total', 0))
            order.status = str(item.get('status', 'pending'))
            
            if 'customer' in item and item['customer']:
                order.customer_name = item['customer'].get('name', 'غير معروف')
            
            order.raw_data = item 
            db.session.add(order)
            count += 1
        
        db.session.commit()
        print(f"DEBUG: تمت المزامنة بنجاح، عدد الطلبات المضافة: {count}")
