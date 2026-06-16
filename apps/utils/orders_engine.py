# 📂 apps/utils/orders_engine.py

# تم التصحيح: استخدام المسار المطلق (Absolute Import)
from apps.utils.bridge_engine import execute_query

def get_pending_orders():
    """
    جلب الطلبات التي تحتاج تسوية من محرك قمرة.
    """
    query = """
    query {
      orders(status: "pending") {
        id
        totalPrice
        lineItems {
          product {
            tags
          }
        }
      }
    }
    """
    result = execute_query(query)
    
    # التأكد من سلامة البيانات قبل إرجاعها
    if not result or 'data' not in result:
        return []
        
    return result.get('data', {}).get('orders', [])
