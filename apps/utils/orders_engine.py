# 📂 apps/utils/orders_engine.py
import logging
from apps.utils.bridge_engine import execute_query

# إعداد الـ logger ليتمكن من طباعة رسائل الـ DEBUG
logger = logging.getLogger(__name__)

def get_pending_orders():
    """
    جلب الطلبات المعلقة مع إضافة سجلات تشخيص لفحص استجابة API قمرة.
    """
    query = """
    query {
      findAllOrders(status: "pending") {
        id
        totalPrice
        lineItems {
          product {
            name
            tags
          }
        }
      }
    }
    """
    try:
        result = execute_query(query)
        
        # [التشخيص] طباعة الـ result كاملة في الـ logs
        # ستظهر هذه الرسالة في لوحة تحكم Render ضمن قسم Logs
        logger.info(f"DEBUG: Qumra API Raw Response: {result}")
        
        if not result or 'data' not in result:
            return []
            
        data = result.get('data', {})
        return data.get('findAllOrders', [])

    except Exception as e:
        logger.error(f"Critical error in get_pending_orders: {str(e)}")
        return []
