# coding: utf-8
# 📂 apps/api/sync_engine.py - محرك المزامنة المتكامل مع منصة قمرة (النسخة النهائية)

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
            "Content-Type": "application/json"
        }

    @staticmethod
    def fetch_and_sync_order():
        """جلب ومزامنة الطلبات من findAllOrders مع كافة الحقول المطلوبة"""
        query = """
        query {
            findAllOrders {
                id
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
            response = requests.post(SyncEngine.API_URL, json={'query': query}, headers=SyncEngine._get_headers())
            result = response.json()
            
            orders_data = result.get('data', {}).get('findAllOrders', [])
            logger.info(f"🔍 [SyncEngine] تم استلام {len(orders_data)} طلب من API.")

            for item in orders_data:
                order_id = str(item['orderId'])
                order = ProcessedOrder.query.get(order_id)
                
                if not order:
                    order = ProcessedOrder(id=order_id)
                
                # تحديث كافة الحقول لتطابق الواجهة
                order.customer_name = item.get('customerName')
                order.items_count = int(item.get('itemsCount', 0))
                order.total_price = float(item.get('total', 0))
                order.status = item.get('status')
                order.shipping_status = item.get('shippingStatus')
                order.shipping_address = item.get('shippingAddress')
                order.payment_method = item.get('paymentMethod')
                order.source = item.get('source')
                
                # تحويل التاريخ
                if item.get('createdAt'):
                    try:
                        date_str = item['createdAt'].replace('Z', '+00:00')
                        order.created_at_api = datetime.fromisoformat(date_str)
                    except Exception:
                        pass
                
                db.session.add(order)
            
            db.session.commit()
            logger.info("✅ تم حفظ الطلبات في قاعدة البيانات بنجاح.")
            return True
        except Exception as e:
            logger.error(f"❌ [SyncEngine] خطأ أثناء المزامنة: {e}")
            db.session.rollback()
            return False

    # دوال الـ Mutations تبقى كما هي لدعم الإجراءات (إلغاء، شحن، تحديث)
    @staticmethod
    def _execute_mutation(mutation, variables):
        try:
            response = requests.post(SyncEngine.API_URL, json={'query': mutation, 'variables': variables}, headers=SyncEngine._get_headers())
            return response.json()
        except Exception as e:
            logger.error(f"❌ [SyncEngine] خطأ Mutation: {e}")
            return None

    @staticmethod
    def cancel_order(order_id):
        mutation = "mutation($id: ID!) { cancelOrder(id: $id) { id status } }"
        return SyncEngine._execute_mutation(mutation, {"id": order_id})

    @staticmethod
    def mark_as_fulfilled(order_id):
        mutation = "mutation($id: ID!) { markOrderFulfilled(id: $id) { id status } }"
        return SyncEngine._execute_mutation(mutation, {"id": order_id})

    @staticmethod
    def update_order_status(order_id, new_status):
        mutation = "mutation($id: ID!, $status: String!) { updateOrderStatus(id: $id, status: $status) { id status } }"
        return SyncEngine._execute_mutation(mutation, {"id": order_id, "status": new_status})
