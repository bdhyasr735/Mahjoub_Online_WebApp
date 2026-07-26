# coding: utf-8
# 📂 apps/admin_Product/__init__.py

"""
موديول إدارة المنتجات
يتضمن:
- عرض المنتجات
- إضافة/تعديل/حذف
- مراجعة المنتجات
- مزامنة مع GraphQL
"""

# استيراد الـ Blueprint من routes
from .routes import admin_product_bp

# استيراد دوال التسجيل من registry
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
    'admin_product_bp',
    'MODULE_NAME',
    'MODULE_ICON',
    'SHOW_IN_SUPPLIER',
    'LINKS',
    'register_module',
    'get_module_stats',
    'get_module_link',
    'get_dashboard_card'
]
