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
    'suppliers_product_bp.products': '📦 منتجاتي',
    'add_product_bp.add_product_page': '➕ إضافة منتج'
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
    try:
        # ✅ استيراد الـ Blueprints من routes
        from apps.suppliers_product.routes import suppliers_product_bp as bp, add_product_bp, edit_product_bp
        
        if 'suppliers_product_bp' not in app.blueprints:
            app.register_blueprint(bp, url_prefix='/supplier')
            print("✅ [Registry]: تم تسجيل 'suppliers_product_bp'")
        
        if 'add_product_bp' not in app.blueprints:
            app.register_blueprint(add_product_bp, url_prefix='/supplier')
            print("✅ [Registry]: تم تسجيل 'add_product_bp'")
        
        if 'edit_product_bp' not in app.blueprints:
            app.register_blueprint(edit_product_bp, url_prefix='/supplier')
            print("✅ [Registry]: تم تسجيل 'edit_product_bp'")
            
    except Exception as e:
        print(f"❌ [Registry]: خطأ في تسجيل suppliers_product: {e}")
    
    return app


def get_module_stats(supplier_id):
    """جلب إحصائيات المنتجات للمورد"""
    try:
        from apps.suppliers_product.services import get_product_stats
        return get_product_stats(supplier_id)
    except:
        return {'total': 0, 'published': 0, 'draft': 0, 'rejected': 0, 'archived': 0, 'has_products': False}


def get_module_link():
    """الحصول على رابط الموديول"""
    return url_for('suppliers_product_bp.products')


def get_dashboard_card(supplier_id):
    """الحصول على بيانات البطاقة للوحة التحكم"""
    stats = get_module_stats(supplier_id)
    
    return {
        'title': MODULE_NAME,
        'icon': MODULE_ICON,
        'link': get_module_link(),
        'stats': stats,
        'color': 'purple',
        'badge': stats.get('total', 0),
        'subtitle': f"{stats.get('published', 0)} منشور، {stats.get('draft', 0)} قيد المراجعة"
    }


__all__ = [
    'MODULE_NAME', 'MODULE_ICON', 'SHOW_IN_SUPPLIER', 'LINKS',
    'suppliers_product_bp', 'register_module',
    'get_module_stats', 'get_module_link', 'get_dashboard_card'
]
