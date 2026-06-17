import requests
from apps.models.orders_db import ProcessedOrder, db
import logging

class SyncEngine:
    API_URL = "https://mahjoub.online/admin/graphql"
    API_TOKEN = "qmr_e063f7f4-ed44-4c86-b105-8405326b9eb9"

    @staticmethod
    def fetch_and_sync_order():
        """جلب الطلبات من قمرا وتحديث قاعدة البيانات المحلية بناءً على الحقول الدقيقة"""
        
        # استعلام GraphQL باستخدام الحقول التي زودتني بها
        query = """
        query {
            orders {
                id
                orderId
                customerName
                itemsCount
                total
                status
                createdAt
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
                # استخدام orderId (المعرف الظاهر) كمفتاح أساسي إذا كان هو المرجع للعميل
                order = ProcessedOrder.query.filter_by(id=str(item['orderId'])).first()
                
                if not order:
                    order = ProcessedOrder(id=str(item['orderId']))
                
                # تحديث الحقول
                order.customer_name = item['customerName']
                order.total_price = float(item['total']) # سيتم تشفيره تلقائياً عبر @setter
                order.status = item['status'] # سيخزن الحالة (paid, pending, etc)
                # ملاحظة: يمكنك إضافة حقل جديد في models/orders_db.py للـ itemsCount إذا أردت
                
                db.session.add(order)
            
            db.session.commit()
            return True
        except Exception as e:
            logging.error(f"❌ Sync Engine Error: {e}")
            db.session.rollback()
            return False
