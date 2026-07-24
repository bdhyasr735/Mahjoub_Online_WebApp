# coding: utf-8
# 📂 apps/suppliers_product/registry.py

from flask import url_for
from apps.suppliers_product.routes import suppliers_product_bp, add_product_bp, edit_product_bp

MODULE_NAME = "منتجاتي"
MODULE_ICON = "fas fa-boxes"
SHOW_IN_SUPPLIER = True
LINKS = {'suppliers_product_bp.products': '📦 منتجاتي'}


def register_module(app):
    """تسجيل الموديول في التطبيق"""
    try:
        app.register_blueprint(suppliers_product_bp, url_prefix='/supplier')
        app.register_blueprint(add_product_bp, url_prefix='/supplier')
        app.register_blueprint(edit_product_bp, url_prefix='/supplier')
        print("✅ [Registry]: تم تسجيل موديول 'منتجاتي'")
    except Exception as e:
        print(f"❌ [Registry]: خطأ في تسجيل موديول منتجاتي: {e}")
    return app


def get_module_stats(supplier_id):
    from apps.suppliers_product.services import get_product_stats
    return get_product_stats(supplier_id)


def get_module_link():
    return url_for('suppliers_product_bp.products')


def get_dashboard_card(supplier_id):
    stats = get_module_stats(supplier_id)
    return {
        'title': MODULE_NAME,
        'icon': MODULE_ICON,
        'link': get_module_link(),
        'stats': stats,
        'color': 'purple',
        'badge': stats.get('total', 0),
        'subtitle': f"{stats.get('published', 0)} منشور"
    }
