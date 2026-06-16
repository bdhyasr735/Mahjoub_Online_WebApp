# 📂 apps/utils/products_engine.py

# استخدام المسارات المطلقة (Absolute Imports) دائماً
from apps.utils.bridge_engine import execute_query
from apps.utils.translator import translate_to_arabic

def get_products_by_supplier(supplier_tag):
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
    
    if not result or 'data' not in result:
        return []
        
    products = result.get('data', {}).get('products', [])
    
    # معالجة الترجمة
    for p in products:
        if 'title' in p and p['title']:
            p['title'] = translate_to_arabic(p['title'])
            
    return products
