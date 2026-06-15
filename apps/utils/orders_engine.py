# 📂 apps/utils/orders_engine.py
import hashlib
from .bridge_engine import QumraBridgeEngine
from apps.extensions import db
from apps.models.order_db import Order
import logging

logger = logging.getLogger(__name__)

class OrdersEngine:
    def __init__(self):
        self.bridge = QumraBridgeEngine()

    def sync_orders_to_db(self):
        """جلب الطلبات من قمرة ومزامنتها مع قاعدة البيانات"""
        query = """
        query {
          orders(first: 20) {
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
        result = self.bridge.execute_query(query)
        orders = result.get("data", {}).get("orders", {}).get("data", [])
        
        if not orders:
            logger.warning("لم يتم العثور على طلبات جديدة.")
            return 0

        count = 0
        for item in orders:
            # توليد معرف فريد (بصمة) إذا لم يتوفر _id
            data_str = f"{item.get('totalPrice')}-{item.get('createdAt')}-{item.get('account', {}).get('name')}"
            fingerprint = hashlib.md5(data_str.encode()).hexdigest()
            qumra_id = str(item.get('_id') or fingerprint)
            
            # البحث عن الطلب أو إنشاؤه (Upsert)
            order = Order.query.filter_by(order_id_qumra=qumra_id).first()
            if not order:
                order = Order(order_id_qumra=qumra_id)
                db.session.add(order)
            
            # تحديث البيانات
            order.total = float(item.get('totalPrice', 0))
            order.status = item.get('status', {}).get('name', 'pending')
            order.customer_name = item.get('account', {}).get('name', 'غير معروف')
            
            count += 1
        
        db.session.commit()
        logger.info(f"تمت مزامنة {count} طلب.")
        return count
