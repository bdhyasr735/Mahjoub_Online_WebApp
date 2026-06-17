# coding: utf-8
# 📂 apps/api/sync_engine.py - محرك المزامنة المتكامل مع منصة قمرة (نسخة التشخيص الكامل)

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
        """جلب ومزامنة الطلبات مع تحليل دقيق للأخطاء"""
        query = """
        query {
            findAllOrders {
                orderId
                customerName
                itemsCount
                total
                status
                shippingStatus
                shippingAddress
                paymentMethod
                source
                createdAt
            }
        }
        """
        try:
            response = requests.post(
                SyncEngine.API_URL, 
                json={'query': query}, 
                headers=SyncEngine._get_headers(),
                timeout=10 # إضافة وقت انتظار لتجنب تعليق النظام
            )
            
            # التحقق من حالة الاتصال
            if response.status_code != 200:
                logger.error(f"❌ [SyncEngine] فشل الاتصال. حالة الـ HTTP: {response.status_code}")
                return False

            result = response.json()
            
            # تحليل الأخطاء داخل الـ GraphQL
            if 'errors' in result:
                logger.error(f"❌ [SyncEngine] خطأ من API قمرة: {result['errors']}")
                return False
            
            # سطر التشخيص (سوف يظهر في Log التابع لـ Render)
            logger.info(f"DEBUG_RESPONSE: {result}") 
            
            orders_data = result.get('data', {}).get('findAllOrders', [])
            
            if orders_data is None or len(orders_data) == 0:
                logger.warning("⚠️ [SyncEngine] الـ API لم يرجع أي طلبات (قد يكون المتجر فارغاً في الـ Sandbox).")
                return False

            logger.info(f"🔍 [SyncEngine] تم استلام {len(orders_data)} طلب.")

            for item in orders_data:
                order_id = str(item.get('orderId'))
                if not order_id: continue
                
                order = ProcessedOrder.query.get(order_id)
                if not order:
                    order = ProcessedOrder(id=order_id)
                
                order.customer_name = item.get('customerName')
                order.items_count = int(item.get('itemsCount', 0))
                order.total_price = float(item.get('total', 0))
                order.status = item.get('status')
                order.shipping_status = item.get('shippingStatus')
                order.shipping_address = item.get('shippingAddress')
                order.payment_method = item.get('paymentMethod')
                order.source = item.get('source')
                
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
            logger.error(f"❌ [SyncEngine] خطأ تقني غير متوقع: {str(e)}")
            db.session.rollback()
            return False

    # ... (بقية دوال الـ Mutation كما هي)
