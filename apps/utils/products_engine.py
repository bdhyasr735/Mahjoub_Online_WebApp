# 📂 apps/utils/products_engine.py

from apps.utils.bridge_engine import execute_query
from apps.utils.translator import translate_to_arabic
# تأكد من استيراد نموذج قاعدة البيانات الخاص بك هنا للمزامنة
from apps.models.product_db import Product 
from apps.extensions import db

def get_products_by_supplier(supplier_tag):
    """جلب منتجات المورد من المحرك مع ترجمة العناوين للعربية."""
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
    
    products = result.get('data', {}).get('products', []) if result else []
    
    # معالجة الترجمة (مع الـ Caching المدمج في المترجم)
    for p in products:
        if 'title' in p and p['title']:
            p['title'] = translate_to_arabic(p['title'])
    return products

def sync_products_to_db():
    """دالة المزامنة السيادية: جلب المنتجات وتحديث قاعدة البيانات المحلية."""
    # هنا يتم جلب البيانات من قمرة
    raw_products = get_products_by_supplier("all") 
    count = 0
    
    for item in raw_products:
        # البحث عن المنتج في قاعدة البيانات المحلية أو إنشاؤه
        product = Product.query.filter_by(external_id=item['id']).first()
        if not product:
            product = Product(external_id=item['id'])
            db.session.add(product)
        
        # تحديث البيانات (مترجمة وجاهزة)
        product.title = item['title']
        product.status = item['status']
        count += 1
        
    db.session.commit()
    return count
