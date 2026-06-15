# 📂 apps/utils/orders_engine.py
from flask import current_app
from apps.extensions import db
from apps.models.order_db import Order
import logging
import requests

logger = logging.getLogger(__name__)

class OrdersEngine:
    def __init__(self):
        self.api_url = "https://mahjoub.online/admin/graphql"
        self.api_key = "qmr_e063f7f4-ed44-4c86-b105-8405326b9eb9"
        self.headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    def fetch_orders_from_qumra(self):
        # الاستعلام المحدث بناءً على التوثيق (استخدام input)
        payload = {
            "query": """
            query {
                findAllOrders(input: { limit: 50, page: 1 }) {
                    data {
                        _id
                        total
                        status
                        customer {
                            name
                        }
                    }
                }
            }
            """
        }
        try:
            response = requests.post(self.api_url, json=payload, headers=self.headers, timeout=15)
            result = response.json()
            
            # تسجيل الرد للتأكد
            logger.info(f"🔍 رد السيرفر بعد تعديل الاستعلام: {result}")
            
            # استخراج البيانات من المسار الصحيح
            return result.get('data', {}).get('findAllOrders', {}).get('data', [])
        except Exception as e:
            logger.error(f"❌ خطأ في الاتصال: {str(e)}")
            return []

    def sync_orders_to_db(self):
        orders = self.fetch_orders_from_qumra()
        logger.info(f"🔍 تم جلب {len(orders)} طلب من قمرة.")
        
        count = 0
        for item in orders:
            order_id = str(item.get('_id'))
            if not order_id or order_id == "None": continue
            
            order = Order.query.filter_by(order_id_qumra=order_id).first() or Order(order_id_qumra=order_id)
            
            # تعبئة الأعمدة الأساسية
            order.total = float(item.get('total', 0))
            order.status = str(item.get('status', 'pending'))
            
            # تعبئة العميل
            if 'customer' in item and item['customer']:
                order.customer_name = item['customer'].get('name', 'غير معروف')
            
            # حفظ كامل الـ Object في raw_data
            order.raw_data = item 
            
            db.session.add(order)
            count += 1
        
        db.session.commit()
        logger.info(f"🚀 تمت مزامنة {count} طلب.")
