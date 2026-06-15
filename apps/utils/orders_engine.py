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
        print("DEBUG: محاولة الاتصال بـ API قمرة - جلب معرفات الطلبات...")
        # طلب _id فقط لتجنب أخطاء حقول التوثيق الصارمة
        payload = {
            "query": """
            query {
                findAllOrders(input: { limit: 50, page: 1 }) {
                    data {
                        _id
                    }
                }
            }
            """
        }
        try:
            response = requests.post(self.api_url, json=payload, headers=self.headers, timeout=15)
            result = response.json()
            
            # طباعة الرد الخام لمعرفة الحقول المتوفرة فعلياً في الـ Response
            print(f"DEBUG: رد السيرفر الخام (استكشاف): {result}")
            
            orders = result.get('data', {}).get('findAllOrders', {}).get('data', [])
            print(f"DEBUG: تم جلب {len(orders)} طلب.")
            return orders
        except Exception as e:
            print(f"DEBUG: خطأ أثناء الاتصال: {str(e)}")
            return []

    def sync_orders_to_db(self):
        print("DEBUG: بدء عملية المزامنة...")
        orders = self.fetch_orders_from_qumra()
        
        count = 0
        for item in orders:
            # استخدام _id كمعرف فريد للربط
            order_id = str(item.get('_id'))
            if not order_id or order_id == "None": continue
            
            # البحث في قاعدة بيانات محجوب أونلاين
            order = Order.query.filter_by(order_id_qumra=order_id).first() or Order(order_id_qumra=order_id)
            
            # بما أننا جلبنا _id فقط، نحفظ كامل الكائن في raw_data للرجوع إليه لاحقاً
            order.raw_data = item 
            
            db.session.add(order)
            count += 1
        
        db.session.commit()
        print(f"DEBUG: تمت المزامنة بنجاح، عدد الطلبات المعالجة: {count}")
