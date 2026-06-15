# 📂 apps/utils/orders_engine.py
from .bridge_engine import QumraBridgeEngine
from apps.extensions import db
from apps.models.order_db import Order

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
        """مزامنة الطلبات من قمرة (مع دعم الصفحات)"""
        # ملاحظة: قم بتعديل الـ query لتشمل وسيط الترقيم في قمرة إذا كان متاحاً
        query = """
        query {
            orders(first: 20, page: %d) {
                data {
                    _id totalPrice status { name } account { name } createdAt
                }
            }
        }
        """ % page
        
        result = self.execute_query(query)
        data = result.get("data", {}).get("orders", {}).get("data", [])
        
        count = 0
        for item in data:
            order_id = str(item.get('_id'))
            order = Order.query.filter_by(order_id_qumra=order_id).first() or Order(order_id_qumra=order_id)
            
            order.total = float(item.get('totalPrice', 0))
            order.status = item.get('status', {}).get('name', 'pending')
            order.customer_name = item.get('account', {}).get('name', 'غير معروف')
            # تأكد أن الموديل يحتوي على حقل created_at
            
            db.session.add(order)
            count += 1
            
        db.session.commit()
        return count
