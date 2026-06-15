# 📂 apps/utils/orders_engine.py
from flask import current_app
from apps.extensions import db
from apps.models.order_db import Order
import logging
import requests

logger = logging.getLogger(__name__)

class OrdersEngine:
    def __init__(self):
        self.api_url = current_app.config.get('QUMRA_API_KEY_URL', "https://mahjoub.online/admin/graphql")
        self.api_key = current_app.config.get('QUMRA_API_KEY')
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def fetch_orders_from_qumra(self):
        """جلب الطلبات مع تجربة أسماء دوال متعددة (Fallback Strategy)"""
        # الاحتمالات الأكثر شيوعاً في واجهات GraphQL الخاصة بالمتاجر
        possible_queries = ["orders", "allOrders", "merchantOrders", "orderList"]
        
        # حقول الطلب التي نريدها (تأكد من تطابقها مع قاعدة بياناتك)
        fields = "_id total status customer { name }"
        
        for q_name in possible_queries:
            query = {"query": f"query {{ {q_name} {{ {fields} }} }}"}
            
            try:
                response = requests.post(self.api_url, json=query, headers=self.headers, timeout=10)
                result = response.json()
                
                # التحقق من أن الاستجابة تحتوي على بيانات وليس خطأ "Field not found"
                if 'errors' not in result and result.get('data', {}).get(q_name):
                    logger.info(f"✅ تم العثور على الدالة الصحيحة: {q_name}")
                    return result['data'][q_name]
                
            except Exception as e:
                logger.warning(f"⚠️ فشل محاولة استخدام {q_name}: {str(e)}")
                continue
        
        logger.error("❌ فشل العثور على أي دالة صالحة لجلب الطلبات.")
        return []

    def sync_orders_to_db(self):
        """مزامنة الطلبات من قمرة إلى قاعدة البيانات المحلية"""
        orders = self.fetch_orders_from_qumra()
        
        if not orders:
            logger.warning("لم يتم جلب أي طلبات.")
            return

        count = 0
        for item in orders:
            # التحقق من وجود الطلب لمنع التكرار
            order_id = str(item.get('_id'))
            if not Order.query.filter_by(order_id=order_id).first():
                new_order = Order(
                    order_id=order_id,
                    total=item.get('total'),
                    status=item.get('status')
                )
                db.session.add(new_order)
                count += 1
        
        db.session.commit()
        logger.info(f"🚀 تمت مزامنة {count} طلب جديد بنجاح.")
