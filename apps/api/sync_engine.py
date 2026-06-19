# coding: utf-8
import requests
import logging
from apps.extensions import db

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
        from apps.models import ProcessedOrder
        
        logger.info("🔄 بدء المزامنة المطابقة لهيكل QumraQL...")
        
        # استعلام محدث يطابق الهيكل الجديد (Metrics & Dimensions & Details)
        query = """
        query {
            findAllOrders {
                data {
                    qid
                    orderId
                    totalPrice
                    orderStatus
                    financialStatus
                    fulfillmentStatus
                    customerPhone
                    items { title qty subtotal }
                    shipping { city district street }
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
                # نستخدم qid كمعرف فريد أساسي (Primary Key)
                unique_id = str(item.get('qid'))
                if not unique_id: continue
                
                order = ProcessedOrder.query.filter_by(id=unique_id).first() or ProcessedOrder(id=unique_id)
                
                # تحديث الحقول الأساسية
                order.order_id = item.get('orderId')
                order.total_price = float(item.get('totalPrice') or 0.0)
                order.order_status = item.get('orderStatus')
                order.financial_status = item.get('financialStatus')
                order.fulfillment_status = item.get('fulfillmentStatus')
                order.customer_phone = item.get('customerPhone')
                
                # تفاصيل الشحن
                ship = item.get('shipping') or {}
                order.shipping_city = ship.get('city')
                order.shipping_street = ship.get('street')
                
                db.session.add(order)
                sync_count += 1
            
            db.session.commit()
            logger.info(f"✅ تمت مزامنة {sync_count} طلب بنجاح حسب مواصفات QumraQL.")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ خطأ فني أثناء المزامنة: {str(e)}")
            return False
