from bridge_engine import execute_query

def get_pending_orders():
    # جلب الطلبات التي تحتاج تسوية
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
    return result.get('data', {}).get('orders', []) if result else []
