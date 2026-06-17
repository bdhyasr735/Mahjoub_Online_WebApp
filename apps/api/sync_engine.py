# coding: utf-8
# 📂 apps/api/sync_engine.py - محرك المزامنة المستقل

import logging
# تصحيح الاستيراد: من المجلد الجذر وليس من داخل مجلد apps
from config import Config
from apps.extensions import db
from apps.models.orders_db import ProcessedOrder

logger = logging.getLogger(__name__)

class SyncEngine:
    """
    محرك مستقل لمعالجة ومزامنة البيانات.
    يتم استخدامه داخل الويب هوك أو المهام الخلفية.
    """
    
    @staticmethod
    def sync_order_data(order_data):
        """
        يقوم بمعالجة بيانات الطلب وحفظها في قاعدة البيانات.
        """
        try:
            order_id = str(order_data.get('id', ''))
            if not order_id:
                return False

            # البحث عن الطلب أو إنشاء جديد
            order = ProcessedOrder.query.get(order_id)
            if not order:
                order = ProcessedOrder(id=order_id)

            # تحديث الحالة
            order.status = order_data.get('status', 'pending')
            
            # تحديث القيمة المالية (سيقوم الـ setter في الموديل بالتشفير تلقائياً)
            total_amount = order_data.get('total', {}).get('amount', 0.0)
            order.total_price = float(total_amount)

            db.session.add(order)
            db.session.commit()
            
            logger.info(f"🔄 [SyncEngine] تمت مزامنة الطلب {order_id} بنجاح.")
            return True
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ [SyncEngine] خطأ أثناء المزامنة: {e}")
            return False
