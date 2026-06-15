# 📂 apps/utils/orders_engine.py
from apps.extensions import db
from apps.models.order_db import Order
import logging

logger = logging.getLogger(__name__)

class OrdersEngine:
    def sync_orders_to_db(self):
        """
        تعديل المزامنة لتتوافق مع هيكل بيانات قمرة المكتشف
        """
        # ملاحظة: استبدل هذا المسار بالـ API الخاص بك إذا كنت تستخدم engine خارجي
        # هنا نفترض أن fetch_all_orders تعيد القائمة من API قمرة مباشرة
        raw_orders = self.get_latest_orders_from_api() 
        
        for o in raw_orders:
            # استخدام orderId كما حدده المساعد
            order_id = str(o.get('orderId'))
            
            existing = Order.query.filter_by(order_id_qumra=order_id).first()
            if not existing:
                # مطابقة الحقول المسطحة الجديدة (customerName بدلاً من customer.name)
                new_order = Order(
                    order_id_qumra=order_id,
                    customer_name=o.get('customerName', 'غير معروف'),
                    total=float(o.get('totalPriceWithTax', 0)),
                    status=o.get('status', 'pending')
                    # يمكنك إضافة المزيد هنا بناءً على المساعد
                )
                db.session.add(new_order)
        
        db.session.commit()
        logger.info("تمت مزامنة الطلبات بنجاح بناءً على الهيكل الجديد")

    def get_latest_orders_from_api(self):
        # ضع هنا كود الـ requests أو الـ GraphQL الذي يستخدم الـ API Token
        # وتأكد أنك تجلب الحقول التي ذكرها المساعد: orderId, customerName, totalPriceWithTax
        pass
