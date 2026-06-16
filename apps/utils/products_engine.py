# 📂 apps/utils/products_engine.py

# الاستيرادات الآمنة (التي لا تسبب دائرة استيراد) تبقى في الأعلى
from apps.utils.bridge_engine import execute_query
from apps.utils.translator import translate_to_arabic

def get_products_by_supplier(supplier_tag):
    """
    جلب منتجات المورد من المحرك، مع معالجة العناوين للغة العربية.
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
    
    result = execute_query(query, variables)
    
    if not result or 'data' not in result:
        return []
        
    products = result.get('data', {}).get('products', [])
    
    # معالجة الترجمة للعناوين
    for p in products:
        if 'title' in p and p['title']:
            p['title'] = translate_to_arabic(p['title'])
            
    return products

def sync_products_to_db():
    """
    دالة المزامنة: يتم استيراد الموديلات وقاعدة البيانات هنا داخل الدالة 
    لتجنب خطأ Circular Import (خطأ Status 1).
    """
    from apps.models.product_db import Product
    from apps.extensions import db
    
    raw_products = get_products_by_supplier("all") 
    count = 0
    
    for item in raw_products:
        # البحث عن المنتج في قاعدة البيانات أو إنشاؤه
        product = Product.query.filter_by(external_id=item['id']).first()
        if not product:
            product = Product(external_id=item['id'])
            db.session.add(product)
        
        # تحديث البيانات
        product.title = item['title']
        product.status = item['status']
        count += 1
        
    db.session.commit()
    return count

def get_product_status_translation(status):
    """مترجم سريع للحالات البرمجية للمنتجات."""
    translations = {
        'active': 'مُفعل',
        'archived': 'مؤرشف',
        'draft': 'مسودة',
        'retired': 'متوقف'
    }
    return translations.get(status.lower(), status)
