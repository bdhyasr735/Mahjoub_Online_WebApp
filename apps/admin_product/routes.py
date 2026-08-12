# coding: utf-8
# 📂 apps/admin_products/registry.py

MODULE_NAME = 'إدارة المنتجات'
MODULE_ICON = 'fas fa-box'
SHOW_IN_SUPPLIER = False

LINKS = {
    'admin_products_bp.list_products': 'قائمة المنتجات',
}

def register_module(app):
    from apps.admin_products.routes import admin_products_bp # عدّل المسار حسب اسم ملف الـ routes لديك
    app.register_blueprint(admin_products_bp)
    print("✅ [Module]: تم تفعيل موديول إدارة المنتجات بنجاح.")
