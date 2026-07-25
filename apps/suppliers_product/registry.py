# coding: utf-8
# 📂 apps/suppliers_product/registry.py

"""
تسجيل تطبيق إدارة منتجات المورد في المنصة مع القائمة المنسدلة الاحترافية
"""

MODULE_NAME = "إدارة المنتجات"
MODULE_ICON = "fas fa-box"
SHOW_IN_SUPPLIER = True

# ✅ مطابقة أسماء الـ Endpoints تماماً لما هو موجود في routes.py
LINKS = {
    'suppliers_product_bp.products': '📦 قائمة المنتجات',
    'add_product_bp.add_product_page': '➕ رفع منتج جديد'
}


def register_module(app):
    """تسجيل تطبيق منتجات المورد والـ Blueprints الخاصة به"""
    try:
        from apps.suppliers_product.routes import (
            suppliers_product_bp,
            add_product_bp,
            edit_product_bp
        )
        
        # 1. تسجيل Blueprint عرض المنتجات
        if 'suppliers_product_bp' not in app.blueprints:
            app.register_blueprint(suppliers_product_bp, url_prefix='/supplier')

        # 2. تسجيل Blueprint إضافة المنتجات
        if 'add_product_bp' not in app.blueprints:
            app.register_blueprint(add_product_bp, url_prefix='/supplier')

        # 3. تسجيل Blueprint تعديل المنتجات
        if 'edit_product_bp' not in app.blueprints:
            app.register_blueprint(edit_product_bp, url_prefix='/supplier')
            
        print("✅ [Registry]: تم تسجيل موديول 'suppliers_product' بنجاح مع القائمة المنسدلة.")
            
    except Exception as e:
        print(f"❌ [Registry]: خطأ في تسجيل موديول suppliers_product: {e}")
    
    return app
