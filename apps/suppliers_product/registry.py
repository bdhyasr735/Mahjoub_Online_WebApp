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

# ✅ الروابط (تظهر في القائمة الجانبية)
LINKS = {
    'suppliers_product_bp.products': '📦 منتجاتي',
    'add_product_bp.add_product_page': '➕ إضافة منتج'
}


def register_module(app):
    """
    تسجيل الموديول في التطبيق
    يتم استدعاؤها تلقائياً من apps/__init__.py
    """
    try:
        # ✅ استيراد الـ Blueprints من routes
        from apps.suppliers_product.routes import suppliers_product_bp, add_product_bp, edit_product_bp
        
        # ✅ تسجيل الـ Blueprints في التطبيق
        app.register_blueprint(suppliers_product_bp, url_prefix='/supplier')
        app.register_blueprint(add_product_bp, url_prefix='/supplier')
        app.register_blueprint(edit_product_bp, url_prefix='/supplier')
        
        print("✅ [Registry]: تم تسجيل موديول 'منتجاتي' بنجاح.")
        print("   📌 Blueprints: suppliers_product_bp, add_product_bp, edit_product_bp")
        
    except ImportError as e:
        print(f"❌ [Registry]: خطأ في استيراد routes: {e}")
    except Exception as e:
        print(f"❌ [Registry]: خطأ في تسجيل suppliers_product: {e}")
    
    return app


def get_module_stats(supplier_id):
    """جلب إحصائيات المنتجات للمورد (للوحة التحكم)"""
    try:
        from apps.suppliers_product.services import get_product_stats
        return get_product_stats(supplier_id)
    except Exception as e:
        print(f"❌ خطأ في get_module_stats: {e}")
        return {
            'total': 0,
            'published': 0,
            'draft': 0,
            'rejected': 0,
            'archived': 0,
            'has_products': False
        }


def get_module_link():
    """الحصول على رابط الصفحة الرئيسية للموديول"""
    return url_for('suppliers_product_bp.products')


def get_dashboard_card(supplier_id):
    """الحصول على بيانات البطاقة لعرضها في لوحة التحكم"""
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


# ============================================================
# ✅ تصدير الدوال الأساسية
# ============================================================

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
