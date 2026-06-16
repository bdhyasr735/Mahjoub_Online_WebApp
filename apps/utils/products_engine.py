# 📂 apps/utils/orders_engine.py
import logging
from apps.utils.bridge_engine import execute_query

logger = logging.getLogger(__name__)

def get_pending_orders():
    """
    جلب الطلبات مباشرة من قمرة لفرز الحالات المعلقة حياً ومباشراً في الذاكرة العشوائية.
    متوافق مع بنية PaginatedOrdersResponse لمتجر قمرة.
    """
    # الاستعلام يلتف الآن داخل كائن data لتفادي خطأ PaginatedOrdersResponse
    query = """
    query GetPendingOrders {
      findAllOrders {
        data {
          id
          totalPrice
          status
          createdAt
          lineItems {
            id
            product {
              id
              name
            }
          }
        }
      }
    }
    """
    result = execute_query(query)
    
    if not result or 'data' not in result:
        return []
        
    response_data = result.get('data', {})
    paginated_response = response_data.get('findAllOrders') or {}
    
    # استخراج مصفوفة الطلبات الحية من كائن التصفيف
    orders = []
    if isinstance(paginated_response, dict):
        orders = paginated_response.get('data') or paginated_response.get('nodes') or []
    elif isinstance(paginated_response, list):
        orders = paginated_response

    if not isinstance(orders, list):
        return []

    pending_orders_list = []
    for o in orders:
        if isinstance(o, dict) and o.get('status') == 'pending':
            if 'lineItems' not in o or o['lineItems'] is None:
                o['lineItems'] = []
            pending_orders_list.append(o)
            
    return pending_orders_list
    
