# -*- coding: utf-8 -*-
# 📂 apps/admin_Product/registry.py

MODULE_NAME = "إدارة المنتجات"
MODULE_ICON = "fas fa-box-seam" # تم تحديث الأيقونة لتكون متوافقة مع FontAwesome
SHOW_IN_SUPPLIER = False

# الحل الأفضل: استخدام قاموس (Dict) مباشرة لضمان توافقه مع المحرك
LINKS = {
    'admin_Product.list_products': 'جميع المنتجات',
    'admin_Product.create_product': 'إضافة منتج جديد'
}

def register_module(app):
    from apps.admin_Product.routes import admin_product_bp
    if 'admin_Product' not in app.blueprints:
        app.register_blueprint(admin_product_bp, url_prefix='/admin/products')
