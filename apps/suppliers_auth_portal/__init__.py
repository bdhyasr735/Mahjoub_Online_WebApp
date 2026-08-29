# coding: utf-8
# 📂 apps/suppliers_auth_portal/__init__.py

from flask import Blueprint

# ✅ استيراد أدوات الأمان
from .security import PasswordHasher, CSRFProtector

suppliers_auth_bp = Blueprint(
    'suppliers_auth_bp',
    __name__,
    url_prefix='/suppliers',
    template_folder='templates',
    static_folder='static'
)

# استيراد المسارات
from . import routes

__all__ = [
    'suppliers_auth_bp',
    'PasswordHasher',
    'CSRFProtector',
]
