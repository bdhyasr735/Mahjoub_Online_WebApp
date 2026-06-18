# coding: utf-8
import requests
import logging
from apps.models.orders_db import ProcessedOrder, db
from apps.models.sync_log import SyncLog
from datetime import datetime

logger = logging.getLogger(__name__)

class SyncEngine:
    API_URL = "https://mahjoub.online/admin/graphql"  
    API_TOKEN = "qmr_e063f7f4-ed44-4c86-b105-8405326b9eb9"

    @staticmethod
    def _get_headers():
        return {
            "Authorization": f"Bearer {SyncEngine.API_TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "apollo-require-preflight": "true"
        }

    @staticmethod
    def fetch_and_sync_order():
        logger.info("🔄 بدء المزامنة...")
        
        # استعلام أساسي وآمن لتجنب أخطاء GraphQL
        query = """
        query GetOrders {
            findAllOrders {
                data {
                    _id
                    totalPrice
                    createdAt
                }
            }
        }
        """
        
        try:
            response = requests.post(SyncEngine.API_URL, json={'query': query}, headers=SyncEngine._get_headers(), timeout=120)
            result = response.json()
            
            if 'errors' in result:
                logger.error(f"❌ خطأ GraphQL: {result['errors']}")
                return False
            
            orders_data = result.get('data', {}).get('findAllOrders', {}).get('data', [])
            
            for item in orders_data:
                # استخدام _id كمعرف وحيد للطلب لتجنب مشاكل Null
                id_api = item.get('_id')
                if not id_api: continue
                    
                order = ProcessedOrder.query.get(id_api) or ProcessedOrder(id=id_api)
                
                # إسناد القيم الإجبارية لتجنب NotNullViolation
                order.order_id = str(id_api) # نستخدم ID السيرفر كـ order_id في حال غياب الرقم التسلسلي
                order.total_price = float(item.get('totalPrice', 0.0))
                order.order_status = 'pending'
                order.source = 'QumraCloud'
                
                db.session.add(order)
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            # تسجيل الفشل في سجلات النظام
            log = SyncLog(status="failed", error_message=str(e))
            db.session.add(log)
            db.session.commit()
            logger.error(f"❌ فشل المزامنة: {e}")
            return False
