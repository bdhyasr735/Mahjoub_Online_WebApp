"""
registry.py: سجل وحدة موديول apps/admin_Product
(www.mahjoub.online)
"""

try:
    from admin_Product import admin_product_bp
except ImportError:
    from . import admin_product_bp

# ✅ جعلنا الموديول يشبه بقية الموديولات العاملة
MODULE_NAME = "إدارة المنتجات"
MODULE_ICON = "fa-box"

# ✅ ربط نقاط النهاية الصحيحة الموجودة في routes.py
LINKS = {
    "admin_Product.list_products": "جميع المنتجات",
    "admin_Product.create_product": "إضافة منتج جديد"
}

def register_module(app):
    """تسجيل موديول admin_Product في تطبيق الـ Flask الرئيسي"""
    if 'admin_Product' not in app.blueprints:
        app.register_blueprint(admin_product_bp)
    return True
