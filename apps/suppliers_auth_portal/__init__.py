"""
apps/suppliers_auth_portal/__init__.py
تهيئة تطبيق بوابة الموردين وموظفيهم
"""

from flask import Blueprint

# إنشاء الـ Blueprint الرئيسي
suppliers_auth_bp = Blueprint(
    'suppliers_auth_bp',
    __name__,
    url_prefix='/suppliers',
    template_folder='templates',
    static_folder='static'
)

# استيراد المسارات
from . import routes

__all__ = ['suppliers_auth_bp']
