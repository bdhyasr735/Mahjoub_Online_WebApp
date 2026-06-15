# 📂 apps/utils/orders_engine.py
from apps.utils.bridge_engine import QumraBridgeEngine
from apps.extensions import db
from apps.models.order_db import Order
import logging

logger = logging.getLogger(__name__)

class OrdersEngine:
    def __init__(self):
        self.bridge = QumraBridgeEngine()

    def sync_orders_to_db(self):
        # نقوم بجلب البيانات
        orders = self.bridge.fetch_latest_orders()
        if not orders: return 0

        count = 0
        for item in orders:
            # 1. المعرف الفريد ضروري
            order_id = str(item.get('_id') or item.get('id') or '')
            if not order_id: continue
            
            # 2. البحث عن الطلب أو إنشاؤه
            order = Order.query.filter_by(order_id_qumra=order_id).first() or Order(order_id_qumra=order_id)
            
            # 3. التسجيل التلقائي (Dynamic Assignment)
            # أي حقل موجود في رد قمرة سنحاول حفظه في قاعدة البيانات
            for key, value in item.items():
                if hasattr(order, key):  # إذا كان هذا العمود موجوداً في قاعدة بياناتك
                    setattr(order, key, value)
            
            # 4. معالجة الحالات الخاصة التي نبهتنا عليها (حالات التداخل)
            order.total = float(item.get('totalPrice') or item.get('total', 0))
            
            db.session.add(order)
            count += 1
            
        db.session.commit()
        return count
