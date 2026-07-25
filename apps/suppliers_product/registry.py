# coding: utf-8
# 📂 apps/suppliers_product/registry.py

"""
تسجيل تطبيق إدارة منتجات المورد في المنصة مع القائمة المنسدلة الاحترافية
"""

MODULE_NAME = "إدارة المنتجات"
MODULE_ICON = "fas fa-box"
SHOW_IN_SUPPLIER = True

LINKS = {
    'suppliers_product.index': '📦 قائمة المنتجات',
    'suppliers_product.add_product': '➕ رفع منتج جديد'
}


def register_module(app):
    """تسجيل تطبيق منتجات المورد والـ Blueprints الخاصة به"""
    try:
        # ✅ استيراد الـ Blueprint الرئيسي الذي يحتوي على كافة مسارات المنتجات
        from apps.suppliers_product.product_routes import suppliers_product_bp
        
        if 'suppliers_product' not in app.blueprints:
            app.register_blueprint(suppliers_product_bp, url_prefix='/supplier')
            
        print("✅ [Registry]: تم تسجيل موديول suppliers_product بنجاح")
            
    except Exception as e:
        print(f"❌ [Registry]: خطأ في تسجيل موديول suppliers_product: {e}")
    
    return app
