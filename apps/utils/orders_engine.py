# 📂 apps/utils/orders_engine.py
import logging
from apps.utils.bridge_engine import execute_query

logger = logging.getLogger(__name__)

def get_pending_orders():
    """
    جلب الطلبات مباشرة من قمرة لفرز الحالات المعلقة حياً ومباشراً في الذاكرة.
    """
    # تعديل الـ Query لتتوافق مع مخطط قمرة لطلب الحقول الأساسية
    query = """
    query GetPendingOrders {
      allOrders {
        id
        totalPrice
        status
        createdAt
      }
    }
    """
    result = execute_query(query)
    
    if not result or 'data' not in result:
        return []
        
    # التحقق من مفتاح الاستعلام الصحيح المرتجع من المخطط
    data = result.get('data', {})
    orders = data.get('allOrders') or data.get('orders') or []
    
    # تصفية الطلبات المعلقة حياً في الذاكرة لسرعة العرض الفورية
    return [o for o in orders if o.get('status') == 'pending']
