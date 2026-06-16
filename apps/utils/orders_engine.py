# 📂 apps/utils/orders_engine.py
import logging
from apps.utils.bridge_engine import execute_query

logger = logging.getLogger(__name__)

def get_pending_orders():
    """
    جلب الطلبات باستخدام الاستعلام الصحيح المتوافق مع API قمرة.
    """
    # الاستعلام المصحح بناءً على صورة الـ Sandbox
    query = """
    query {
      findAllOrders(input: { limit: 20, page: 1 }) {
        data {
          _id
          totalPrice
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
        
        # [التشخيص] طباعة الـ result كاملة في الـ logs
        logger.info(f"DEBUG: Qumra API Raw Response: {result}")
        
        if not result or 'data' not in result:
            return []
            
        # استخراج البيانات من الهيكل الصحيح (data -> findAllOrders -> data)
        orders_wrapper = result.get('data', {}).get('findAllOrders', {})
        return orders_wrapper.get('data', [])

    except Exception as e:
        logger.error(f"Critical error in get_pending_orders: {str(e)}")
        return []
