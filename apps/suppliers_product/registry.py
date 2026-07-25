# coding: utf-8
# 📂 apps/suppliers_product/__init__.py

"""
تطبيق منتجات الموردين
"""

# استيراد كل شيء من registry.py
from .registry import *

# تصدير كل شيء للاستخدام الخارجي
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
