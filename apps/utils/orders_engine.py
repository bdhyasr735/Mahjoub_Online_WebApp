# 📂 apps/utils/orders_engine.py
import logging
from apps.utils.bridge_engine import execute_query

logger = logging.getLogger(__name__)

class OrdersEngine:
    def get_all_orders(self):
        """جلب الطلبات من منصة قمرة مع الحقول المحددة"""
        query = """
        query {
          findAllOrders(input: { limit: 20, page: 1 }) {
            data {
              _id
              customer { name }
              createdAt
              status
              financialStatus
              fulfillmentStatus
              paymentMethod
              totalPrice { amount currency }
              items { productId price quantity }
            }
          }
        }
        """
        try:
            result = execute_query(query)
            # سجل البيانات للتشخيص في حالة عدم ظهور نتائج
            logger.info(f"Qumra API Response: {result}")
            
            if not result or 'data' not in result:
                return []
            return result.get('data', {}).get('findAllOrders', {}).get('data', [])
        except Exception as e:
            logger.error(f"Error fetching orders: {str(e)}")
            return []

    def get_pending_orders(self):
        """تصفية الطلبات المعلقة برمجياً"""
        all_orders = self.get_all_orders()
        return [o for o in all_orders if o.get('status') == 'pending']

def get_pending_orders():
    engine = OrdersEngine()
    return engine.get_pending_orders()
