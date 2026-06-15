# 📂 apps/utils/orders_engine.py
from .bridge_engine import QumraBridgeEngine
from apps.extensions import db
from apps.models.order_db import Order
import logging

logger = logging.getLogger(__name__)

class OrdersEngine(QumraBridgeEngine):

    def get_paginated_orders(self, page=1, per_page=10):
        """جلب الطلبات من قاعدة البيانات المحلية مع الترقيم"""
        return Order.query.order_by(Order.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

    def update_status(self, order_id, new_status):
        """تحديث الحالة محلياً"""
        order = Order.query.get(order_id)
        if order:
            order.status = new_status
            db.session.commit()
            return True
        return False

    def sync_orders_from_source(self, page=1):
        """مزامنة الطلبات من قمرة مع تسجيل الأخطاء للتشخيص"""
        query = """
        query {
            orders(first: 20, page: %d) {
                data {
                    _id
                    totalPrice
                    createdAt
                    status { name }
                    account { name }
                }
            }
        }
        """ % page
        
        result = self.execute_query(query)
        
        # تصحيح: تسجيل النتيجة في سجلات Render لمعرفة لماذا يفشل الاتصال
        logger.info(f"Qumra API Response: {result}")
        
        # التأكد من وجود البيانات قبل المحاولة
        if not result or 'data' not in result or 'orders' not in result.get('data', {}):
            logger.error("فشل في جلب البيانات من قمرة: الاستجابة فارغة أو تحتوي على أخطاء")
            return 0
            
        data = result.get("data", {}).get("orders", {}).get("data", [])
        
        count = 0
        for item in data:
            order_id = str(item.get('_id'))
            order = Order.query.filter_by(order_id_qumra=order_id).first() or Order(order_id_qumra=order_id)
            
            order.total = float(item.get('totalPrice', 0))
            order.status = item.get('status', {}).get('name', 'pending') if item.get('status') else 'pending'
            order.customer_name = item.get('account', {}).get('name', 'غير معروف') if item.get('account') else 'غير معروف'
            
            db.session.add(order)
            count += 1
            
        db.session.commit()
        return count
