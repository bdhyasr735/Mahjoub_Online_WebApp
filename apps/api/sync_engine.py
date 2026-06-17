# coding: utf-8
# 📂 apps/api/sync_engine.py - محرك المزامنة (النسخة الاستقصائية)

import requests
import logging
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
        page = 1
        has_next_page = True
        
        while has_next_page:
            logger.info(f"🔄 جاري جلب الصفحة: {page}")
            
            # نطلب الحقول الأكثر احتمالاً دفعة واحدة
            query = """
            query($page: Int) {
                findAllOrders(input: {page: $page, limit: 10}) {
                    data {
                        _id
                        status {
                            name
                            value
                            label
                            key
                        }
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
                    timeout=30
                )
                
                result = response.json()
                
                # إذا نجحنا، نخرج البيانات
                if 'data' in result and result['data'].get('findAllOrders'):
                    data_wrapper = result['data']['findAllOrders']
                    orders_data = data_wrapper.get('data', [])
                    
                    for item in orders_data:
                        order_id = str(item.get('_id'))
                        order = ProcessedOrder.query.get(order_id) or ProcessedOrder(id=order_id)
                        
                        # محاولة استخراج الحالة من أي حقل متاح
                        status_obj = item.get('status', {})
                        order.status = status_obj.get('name') or status_obj.get('value') or status_obj.get('label') or status_obj.get('key') or 'pending'
                        
                        order.total_price = float(item.get('totalPrice', 0))
                        db.session.add(order)
                    
                    db.session.commit()
                    has_next_page = data_wrapper.get('pagination', {}).get('hasNextPage', False)
                    page += 1
                else:
                    logger.error(f"❌ خطأ في الاستجابة: {result}")
                    return False
                
            except Exception as e:
                db.session.rollback()
                logger.error(f"❌ خطأ برمجي: {str(e)}")
                return False
        return True

    # الدوال الأخرى تبقى كما هي...
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
