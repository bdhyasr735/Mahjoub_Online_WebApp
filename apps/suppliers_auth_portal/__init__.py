# coding: utf-8
# 📂 apps/suppliers_auth_portal/__init__.py

"""
📦 تطبيق بوابة الموردين وموظفيهم
مسؤول عن تسجيل الدخول، التسجيل، استعادة كلمة المرور، والتحقق
"""

from flask import Blueprint

# ✅ استيراد أدوات الأمان
from .security import PasswordHasher, CSRFProtector

# ==================== تعريف Blueprint ====================
suppliers_auth_bp = Blueprint(
    'suppliers_auth_bp',
    __name__,
    url_prefix='/suppliers',
    template_folder='templates',
    static_folder='static'
)

# ==================== استيراد المسارات ====================
from . import routes

# ==================== التصدير ====================
__all__ = [
    'suppliers_auth_bp',
    'PasswordHasher',
    'CSRFProtector',
]
