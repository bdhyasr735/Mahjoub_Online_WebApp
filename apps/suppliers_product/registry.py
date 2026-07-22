# coding: utf-8
# 📂 apps/suppliers_product/registry.py

"""
تسجيل تطبيق منتجات الموردين في المنصة
"""

from flask import Blueprint

# ✅ بيانات الموديول
MODULE_NAME = "منتجاتي"
MODULE_ICON = "fas fa-boxes"
SHOW_IN_SUPPLIER = True

LINKS = {
    'suppliers_product_bp.products': '📦 منتجاتي'
}

suppliers_product_bp = Blueprint(
    'suppliers_product_bp',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/suppliers_product/static'
)


def register_module(app):  # ✅ تغيير اسم الدالة
    from apps.suppliers_product import routes
    if 'suppliers_product_bp' not in app.blueprints:
        app.register_blueprint(suppliers_product_bp, url_prefix='/supplier')
        print("✅ [Registry]: تم تسجيل 'suppliers_product' بنجاح.")
    return app
