# coding: utf-8
# 📂 apps/suppliers_product/registry.py

"""
تسجيل تطبيق منتجات الموردين في المنصة
"""

from flask import url_for

# ✅ بيانات الموديول
MODULE_NAME = "منتجاتي"
MODULE_ICON = "fas fa-boxes"
SHOW_IN_SUPPLIER = True

# ✅ الروابط
LINKS = {
    'suppliers_product_bp.products': '📦 منتجاتي',
    'add_product_bp.add_product_page': '➕ إضافة منتج'
}


def register_module(app):
    """تسجيل الموديول في التطبيق"""
    try:
        from apps.suppliers_product.routes import suppliers_product_bp, add_product_bp, edit_product_bp
        
        app.register_blueprint(suppliers_product_bp, url_prefix='/supplier')
        app.register_blueprint(add_product_bp, url_prefix='/supplier')
        app.register_blueprint(edit_product_bp, url_prefix='/supplier')
        
        print("✅ [Registry]: تم تسجيل موديول 'منتجاتي'")
    except Exception as e:
        print(f"❌ [Registry]: خطأ في تسجيل suppliers_product: {e}")
    
    return app


def get_module_stats(supplier_id):
    """إحصائيات المنتجات للمورد"""
    try:
        from apps.suppliers_product.services import get_product_stats
        return get_product_stats(supplier_id)
    except Exception as e:
        return {'total': 0, 'published': 0, 'draft': 0, 'has_products': False}


def get_module_link():
    """رابط الصفحة الرئيسية"""
    return url_for('suppliers_product_bp.products')


def get_dashboard_card(supplier_id):
    """بطاقة لوحة التحكم"""
    stats = get_module_stats(supplier_id)
    return {
        'title': MODULE_NAME,
        'icon': MODULE_ICON,
        'link': get_module_link(),
        'stats': stats,
        'color': 'purple',
        'badge': stats.get('total', 0)
    }


__all__ = [
    'MODULE_NAME',
    'MODULE_ICON',
    'SHOW_IN_SUPPLIER',
    'LINKS',
    'register_module',
    'get_module_stats',
    'get_module_link',
    'get_dashboard_card'
]
