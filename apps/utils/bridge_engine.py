# 📂 apps/utils/orders_engine.py
import logging
from apps.utils.bridge_engine import execute_query

logger = logging.getLogger(__name__)

class OrdersEngine:
    def get_all_orders(self):
        """
        جلب الطلبات من منصة قمرة مع الحقول المحددة التي تتضمن
        التفاصيل المالية، وتفاصيل العميل، وحالات التجهيز والدفع.
        """
        query = """
        query {
          findAllOrders(input: { limit: 20, page: 1 }) {
            data {
              _id
              customer { 
                name 
              }
              createdAt
              status
              financialStatus
              fulfillmentStatus
              paymentMethod
              totalPrice { 
                amount 
                currency 
              }
              items { 
                productId 
                price 
                quantity 
              }
            }
          }
        }
        """
        try:
            result = execute_query(query)
            
            # [التشخيص] طباعة الـ result في الـ logs للتحقق من وصول البيانات
            logger.info(f"DEBUG: Qumra API Raw Response: {result}")
            
            if not result or 'data' not in result:
                return []
            
            # استخراج البيانات من هيكلية PaginatedOrdersResponse
            return result.get('data', {}).get('findAllOrders', {}).get('data', [])
            
        except Exception as e:
            logger.error(f"Error fetching orders from Qumra: {str(e)}")
            return []

    def get_pending_orders(self):
        """
        دالة لجلب الطلبات المعلقة فقط.
        بما أن الـ API لا يدعم الفلترة المباشرة بحالة 'pending' في الـ query،
        نقوم بفلترتها برمجياً من النتائج المسترجعة.
        """
        all_orders = self.get_all_orders()
        return [o for o in all_orders if o.get('status') == 'pending']

    def sync_orders_from_source(self):
        """مزامنة الطلبات من المصدر إلى النظام المحلي"""
        try:
            orders = self.get_all_orders()
            if orders:
                logger.info(f"Successfully synced {len(orders)} orders.")
                return True
            return False
        except Exception as e:
            logger.error(f"Sync failed: {str(e)}")
            return False

# دالة مساعدة لاستخدامها مباشرة في الـ Routes
def get_pending_orders():
    engine = OrdersEngine()
    return engine.get_pending_orders()
