# 📂 apps/utils/orders_engine.py
import logging
from apps.utils.bridge_engine import execute_query

logger = logging.getLogger(__name__)

def get_pending_orders():
    """
    جلب الطلبات مباشرة من قمرة لفرز الحالات المعلقة حياً ومباشراً في الذاكرة.
    """
    # استخدام الحقل المدعوم رسمياً من سيرفر قمرة: findAllOrders
    query = """
    query GetPendingOrders {
      findAllOrders {
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
    """
    result = execute_query(query)
    
    if not result or 'data' not in result:
        return []
        
    data = result.get('data', {})
    
    # قراءة الحقل الصحيح المرتجع
    orders = data.get('findAllOrders') or []
    
    if not isinstance(orders, list):
        return []

    pending_orders_list = []
    for o in orders:
        if isinstance(o, dict) and o.get('status') == 'pending':
            if 'lineItems' not in o or o['lineItems'] is None:
                o['lineItems'] = []
            pending_orders_list.append(o)
            
    return pending_orders_list
