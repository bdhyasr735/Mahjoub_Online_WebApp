# coding: utf-8
# 📂 apps/api/sync_engine.py - محرك المزامنة المرن (مُحدث للتصحيح)

import requests
import logging
from datetime import datetime
from apps.models.orders_db import ProcessedOrder, db

logger = logging.getLogger(__name__)

class SyncEngine:
    API_URL = "https://mahjoub.online/admin/graphql"
    API_TOKEN = "qmr_e063f7f4-ed44-4c86-b105-8405326b9eb9"

    @staticmethod
    def _get_headers():
        return {
            "Authorization": f"Bearer {SyncEngine.API_TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    @staticmethod
    def fetch_and_sync_order():
        """جلب ومزامنة الطلبات مع كشف هيكل البيانات"""
        query = """
        query {
            findAllOrders {
                data {
                    _id
                    status
                    totalPrice
                    createdAt
                }
            }
        }
        """
        try:
            response = requests.post(
                SyncEngine.API_URL, 
                json={'query': query}, 
                headers=SyncEngine._get_headers(),
                timeout=20
            )
            
            if response.status_code != 200:
                logger.error(f"❌ [SyncEngine] فشل الاتصال. الحالة: {response.status_code}")
                return False

            result = response.json()
            
            # --- تسجيل الهيكل للتشخيص ---
            logger.info(f"🔍 [SyncEngine] الرد الخام: {result}")

            # محاولة مرنة للوصول للبيانات (نحاول أكثر من مسار إذا فشل الأول)
            data_wrapper = result.get('data', {})
            findAllOrders = data_wrapper.get('findAllOrders', {})
            
            # إذا كان الهيكل {'findAllOrders': [...]} وليس {'findAllOrders': {'data': [...]}}
            orders_data = findAllOrders.get('data', []) if isinstance(findAllOrders, dict) else findAllOrders
            
            if not orders_data:
                logger.warning("⚠️ [SyncEngine] لم يتم العثور على طلبات. تأكد من مسار البيانات في الـ JSON أعلاه.")
                return False

            logger.info(f"✅ [SyncEngine] تم العثور على {len(orders_data)} طلب. بدء الحفظ...")

            for item in orders_data:
                order_id = str(item.get('_id'))
                if not order_id: continue
                
                order = ProcessedOrder.query.get(order_id)
                if not order:
                    order = ProcessedOrder(id=order_id)
                
                order.status = item.get('status')
                order.total_price = float(item.get('totalPrice', 0))
                
                created_at = item.get('createdAt')
                if created_at:
                    try:
                        date_str = created_at.replace('Z', '+00:00')
                        order.created_at_api = datetime.fromisoformat(date_str)
                    except: pass
                
                db.session.add(order)
            
            db.session.commit()
            return True

        except Exception as e:
            logger.error(f"❌ [SyncEngine] خطأ استثنائي: {str(e)}")
            db.session.rollback()
            return False
