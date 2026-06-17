# coding: utf-8
# 📂 apps/api/sync_engine.py - محرك المزامنة المحدث (متوافق مع GraphQL)

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
        """جلب ومزامنة الطلبات من كافة الصفحات"""
        page = 1
        has_next_page = True
        
        while has_next_page:
            logger.info(f"🔄 [SyncEngine] جاري جلب الصفحة رقم: {page}")
            
            # الاستعلام المحدث بناءً على توثيق GraphQL
            query = """
            query($page: Int) {
                orders(page: $page, limit: 10) {
                    data {
                        _id
                        status
                        totalPrice
                        createdAt
                    }
                    pagination {
                        hasNextPage
                    }
                }
            }
            """
            try:
                response = requests.post(
                    SyncEngine.API_URL, 
                    json={'query': query, 'variables': {'page': page}}, 
                    headers=SyncEngine._get_headers(),
                    timeout=20
                )
                
                if response.status_code != 200:
                    logger.error(f"❌ [SyncEngine] فشل الاتصال (كود {response.status_code}). الرد: {response.text}")
                    return False

                result = response.json()
                data_wrapper = result.get('data', {}).get('orders', {})
                orders_data = data_wrapper.get('data', [])
                pagination = data_wrapper.get('pagination', {})
                
                has_next_page = pagination.get('hasNextPage', False)

                if not orders_data:
                    logger.warning(f"⚠️ [SyncEngine] الصفحة {page} فارغة أو انتهت البيانات.")
                    break

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
                logger.info(f"✅ [SyncEngine] تم حفظ {len(orders_data)} طلب من الصفحة {page}.")
                page += 1

            except Exception as e:
                logger.error(f"❌ [SyncEngine] خطأ أثناء معالجة الصفحة {page}: {str(e)}")
                db.session.rollback()
                return False
        
        return True

    @staticmethod
    def _execute_mutation(mutation, variables):
        try:
            response = requests.post(SyncEngine.API_URL, json={'query': mutation, 'variables': variables}, headers=SyncEngine._get_headers())
            return response.json() if response.status_code == 200 else None
        except: return None

    @staticmethod
    def cancel_order(order_id):
        return SyncEngine._execute_mutation("mutation($id: ID!) { cancelOrder(id: $id) { _id } }", {"id": order_id})

    @staticmethod
    def mark_as_fulfilled(order_id):
        return SyncEngine._execute_mutation("mutation($id: ID!) { markOrderFulfilled(id: $id) { _id } }", {"id": order_id})

    @staticmethod
    def update_order_status(order_id, new_status):
        return SyncEngine._execute_mutation("mutation($id: ID!, $status: String!) { updateOrderStatus(id: $id, status: $status) { _id } }", {"id": order_id, "status": new_status})
