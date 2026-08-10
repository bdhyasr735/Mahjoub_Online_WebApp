"""
registry.py: سجل وحدة موديول apps/admin_Product
(www.mahjoub.online)
"""

try:
    from admin_Product import admin_product_bp
except ImportError:
    from . import admin_product_bp

MODULE_NAME = "إدارة المنتجات"
MODULE_ICON = "fa-box"

LINKS = {
    "admin_Product.list_products": "جميع المنتجات",
    "admin_Product.create_product": "إضافة منتج جديد"
}

def register_module(app):
    if 'admin_Product' not in app.blueprints:
        app.register_blueprint(admin_product_bp)
    return True
