# coding: utf-8
# 📂 apps/api/sync_engine.py - محرك المزامنة المحدث والمتوافق

import os
import requests
import logging
from apps.extensions import db
from apps.models.orders_db import Order

logger = logging.getLogger(__name__)

class SyncEngine:
    API_URL = "https://mahjoub.online/admin/graphql"  

    @staticmethod
    def _get_headers():
        # جلب المفتاح من متغيرات البيئة في Render
        api_key = os.environ.get("QUMRA_API_KEY", "qmr_e063f7f4-ed44-4c86-b105-8405326b9eb9")
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    @staticmethod
    def fetch_and_sync_order():
        logger.info("🔄 بدء عملية المزامنة مع متجر قمرة...")
        
        # استعلام يغطي جميع الأعمدة المطلوبة
        query = """
        query {
            findAllOrders {
                data {
                    _id
                    orderId
                    totalPrice
                    createdAt
                    status { code }
                    account { firstName lastName }
                    items { id }
                }
            }
        }
        """
        
        try:
            response = requests.post(
                SyncEngine.API_URL, 
                json={'query': query}, 
                headers=SyncEngine._get_headers(), 
                timeout=60
            )
            
            if response.status_code != 200:
                logger.error(f"❌ خطأ اتصال ({response.status_code}): {response.text}")
                return False

            result = response.json()
            orders_data = result.get('data', {}).get('findAllOrders', {}).get('data', [])
            
            sync_count = 0
            for item in orders_data:
                unique_id = str(item.get('_id'))
                if not unique_id: continue
                
                # جلب الطلب أو إنشاء جديد
                order = Order.query.filter_by(id=unique_id).first() or Order(id=unique_id)
                
                # تعيين البيانات بناءً على المواصفات المطلوبة
                order.order_id_display = str(item.get('orderId', ''))
                order.total_price = float(item.get('totalPrice') or 0.0)
                order.created_at = item.get('createdAt')
                order.order_status = item.get('status', {}).get('code', 'pending')
                order.items_count = len(item.get('items', []))
                
                # اسم العميل
                acc = item.get('account') or {}
                order.customer_name = f"{acc.get('firstName', '')} {acc.get('lastName', '')}".strip() or "عميل"
                
                db.session.add(order)
                sync_count += 1
            
            db.session.commit()
            logger.info(f"✅ تمت المزامنة بنجاح لعدد {sync_count} طلب.")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ خطأ فني أثناء المزامنة: {str(e)}")
            return False
