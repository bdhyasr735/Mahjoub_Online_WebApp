# coding: utf-8
# 📂 apps/suppliers_product/registry.py

"""
تسجيل تطبيق منتجات الموردين في المنصة
"""

from flask import Blueprint, url_for

# ✅ بيانات الموديول
MODULE_NAME = "منتجاتي"
MODULE_ICON = "fas fa-boxes"
SHOW_IN_SUPPLIER = True

# ✅ الروابط
LINKS = {
    'suppliers_product_bp.products': '📦 منتجاتي'
}

# ✅ تعريف الـ Blueprint
suppliers_product_bp = Blueprint(
    'suppliers_product_bp',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/suppliers_product/static'
)


def register_module(app):
    """تسجيل الموديول في التطبيق"""
    # ✅ استيراد routes مباشرة (بدون __init__.py)
    from apps.suppliers_product import routes
    
    if 'suppliers_product_bp' not in app.blueprints:
        app.register_blueprint(suppliers_product_bp, url_prefix='/supplier')
        print("✅ [Registry]: تم تسجيل 'suppliers_product' بنجاح.")
    return app


# ============================================================
# ✅ باقي الدوال (get_module_stats, get_module_link, get_dashboard_card)
# ============================================================
# ... (نفس الكود السابق)
