# coding: utf-8
# 📂 apps/suppliers_product/__init__.py

"""
موديول إدارة منتجات الموردين
يتضمن:
- عرض منتجات المورد
- إضافة/تعديل/حذف منتجات المورد
- مراجعة الحالات الخاصة بمنتجات المورد
"""

# استيراد الـ Blueprint من routes
from .routes import suppliers_product_bp

# استيراد دوال التسجيل من registry (إن وجدت أو يتم توفيرها)
try:
    from .registry import (
        MODULE_NAME,
        MODULE_ICON,
        SHOW_IN_SUPPLIER,
        LINKS,
        register_module,
        get_module_stats,
        get_module_link,
        get_dashboard_card
    )
    __all__ = [
        'suppliers_product_bp',
        'MODULE_NAME',
        'MODULE_ICON',
        'SHOW_IN_SUPPLIER',
        'LINKS',
        'register_module',
        'get_module_stats',
        'get_module_link',
        'get_dashboard_card'
    ]
except ImportError:
    __all__ = [
        'suppliers_product_bp'
    ]
