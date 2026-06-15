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
        print("DEBUG: تنفيذ الاستعلام المحدث...")
        # هذا الاستعلام يستخدم الحقول الصحيحة التي اكتشفناها من الـ Schema
        payload = {
            "query": """
            query {
                findAllOrders(input: { limit: 50, page: 1 }) {
                    data {
                        _id
                        totalPrice
                        status { name }
                        account { name }
                        createdAt
                    }
                }
            }
            """
        }
        try:
            response = requests.post(self.api_url, json=payload, headers=self.headers, timeout=15)
            result = response.json()
            
            # استخراج البيانات
            orders = result.get('data', {}).get('findAllOrders', {}).get('data', [])
            print(f"DEBUG: نجحنا في جلب {len(orders)} طلب.")
            return orders
        except Exception as e:
            print(f"DEBUG: خطأ في الجلب: {str(e)}")
            return []

    def sync_orders_to_db(self):
        print("DEBUG: بدء عملية المزامنة وحفظ البيانات...")
        orders = self.fetch_orders_from_qumra()
        count = 0
        for item in orders:
            order_id = str(item.get('_id'))
            if not order_id: continue
            
            # البحث عن الطلب في قاعدة بياناتك
            order = Order.query.filter_by(order_id_qumra=order_id).first() or Order(order_id_qumra=order_id)
            
            # تحديث البيانات بالحقول الصحيحة
            order.total = float(item.get('totalPrice', 0))
            order.status = item.get('status', {}).get('name', 'N/A')
            order.customer_name = item.get('account', {}).get('name', 'N/A')
            order.raw_data = item
            
            db.session.add(order)
            count += 1
        
        db.session.commit()
        print(f"DEBUG: تمت المزامنة بنجاح، تم إضافة/تحديث {count} طلب.")
