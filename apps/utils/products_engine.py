# 📂 apps/utils/products_engine.py

from apps.utils.bridge_engine import execute_query
from apps.utils.translator import translate_to_arabic

def get_products_by_supplier(supplier_tag):
    """
    جلب المنتجات الخاصة بمورد محدد عبر الـ Tag،
    مع معالجة البيانات وترجمة العناوين للعربية تلقائياً.
    """
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
    
    # جلب البيانات من محرك قمرة (Bridge Engine)
    result = execute_query(query, variables)
    
    if not result:
        return []
        
    products = result.get('data', {}).get('products', [])
    
    # معالجة وتجهيز البيانات (ترجمة العناوين)
    for p in products:
        if 'title' in p and p['title']:
            # نستخدم المترجم السيادي مع Caching مدمج
            p['title'] = translate_to_arabic(p['title'])
            
    return products

def get_product_status_translation(status):
    """
    مترجم سريع للحالات البرمجية للمنتجات.
    """
    translations = {
        'active': 'مُفعل',
        'archived': 'مؤرشف',
        'draft': 'مسودة',
        'retired': 'متوقف'
    }
    return translations.get(status.lower(), status)
