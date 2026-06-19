# coding: utf-8
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
            "Content-Type": "application/json"
        }

    @staticmethod
    def fetch_and_sync_order():
        logger.info("🔄 بدء المزامنة المطابقة للتوثيق الجديد...")
        
        # استعلام يستخدم المسارات الصحيحة: account و shippingAddress
        query = """
        query {
            findAllOrders(input: {}) {
                data {
                    _id
                    totalPrice
                    createdAt
                    status { code }
                    items { productId }
                    account { name phone email }
                    shippingAddress { city address1 }
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
                order_id = str(item.get('_id'))
                if not order_id: continue
                
                order = ProcessedOrder.query.filter_by(id=order_id).first() or ProcessedOrder(id=order_id)
                
                # تعبئة البيانات الأساسية
                order.order_id = order_id[-8:]
                order.total_price = float(item.get('totalPrice') or 0.0)
                order.order_status = item.get('status', {}).get('code', 'pending')
                order.items_count = len(item.get('items') or [])
                
                # تعبئة بيانات العميل والشحن من المسارات الجديدة المكتشفة
                acc = item.get('account') or {}
                order.customer_name = acc.get('name')
                order.customer_phone = acc.get('phone')
                
                ship = item.get('shippingAddress') or {}
                order.shipping_city = ship.get('city')
                order.shipping_street = ship.get('address1')
                
                db.session.add(order)
            
            db.session.commit()
            logger.info(f"✅ تمت مزامنة {len(orders_data)} طلب بنجاح وببيانات كاملة.")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ خطأ فني أثناء المزامنة: {str(e)}")
            return False
