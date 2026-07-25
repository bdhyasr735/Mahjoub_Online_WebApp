# coding: utf-8
# 📂 apps/suppliers_product/registry.py

"""
تسجيل تطبيق إدارة منتجات المورد في المنصة مع القائمة المنسدلة الاحترافية
"""

MODULE_NAME = "إدارة المنتجات"
MODULE_ICON = "fas fa-box"
SHOW_IN_SUPPLIER = True

LINKS = {
    'suppliers_product_bp.products': '📦 قائمة المنتجات',
    'add_product_bp.add_product_page': '➕ رفع منتج جديد'
}


def register_module(app):
    """تسجيل تطبيق منتجات المورد والـ Blueprints الخاصة به"""
    try:
        # ✅ استيراد كل Blueprint من ملفه المستقل لضمان السلامة البرمجية
        from apps.suppliers_product.product_routes import suppliers_product_bp
        from apps.suppliers_product.add_product_routes import add_product_bp
        
        # استيراد edit_product_bp من ملفه الخاص إذا كان مفصولاً، أو التعامل معه برمجياً
        try:
            from apps.suppliers_product.edit_product_routes import edit_product_bp
        except ImportError:
            from apps.suppliers_product.product_routes import edit_product_bp

        if 'suppliers_product_bp' not in app.blueprints:
            app.register_blueprint(suppliers_product_bp, url_prefix='/supplier')

        if 'add_product_bp' not in app.blueprints:
            app.register_blueprint(add_product_bp, url_prefix='/supplier')

        if 'edit_product_bp' not in app.blueprints:
            app.register_blueprint(edit_product_bp, url_prefix='/supplier')
            
        print("✅ [Registry]: تم تسجيل موديول suppliers_product بنجاح")
            
    except Exception as e:
        print(f"❌ [Registry]: خطأ في تسجيل موديول suppliers_product: {e}")
    
    return app
