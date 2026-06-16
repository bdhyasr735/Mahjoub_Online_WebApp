from bridge_engine import execute_query

def get_products_by_supplier(supplier_tag):
    # نستخدم فلتر الـ Tags لجلب منتجات مورد محدد
    query = """
    query GetProducts($query: String) {
      products(query: $query) {
        id
        title
        status
        tags
      }
    }
    """
    variables = {"query": f"tags:{supplier_tag}"}
    result = execute_query(query, variables)
    return result.get('data', {}).get('products', []) if result else []
