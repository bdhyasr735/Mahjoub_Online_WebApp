# -*- coding: utf-8 -*-
# 📂 apps/admin_Product/registry.py

MODULE_NAME = "إدارة المنتجات"
MODULE_ICON = "bi-box-seam"
SHOW_IN_SUPPLIER = False

def get_menu_items():
    # هذا هو الربط الذي يبحث عنه __init__.py لإظهار النوافذ
    return [
        {'title': 'جميع المنتجات', 'endpoint': 'admin_Product.list_products'},
        {'title': 'إضافة منتج جديد', 'endpoint': 'admin_Product.create_product'},
    ]

def register_module(app):
    from apps.admin_Product.routes import admin_product_bp
    if 'admin_Product' not in app.blueprints:
        app.register_blueprint(admin_product_bp, url_prefix='/admin/products')
