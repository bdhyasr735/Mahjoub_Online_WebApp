# coding: utf-8
# 📂 apps/suppliers_auth_portal/__init__.py

print("=" * 50)
print("🚀 [DEBUG] suppliers_auth_portal/__init__.py is being loaded!")
print("=" * 50)

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

print(f"✅ [DEBUG] Blueprint created: {suppliers_auth_bp.name}")

# ==================== استيراد المسارات ====================
from . import routes

print(f"✅ [DEBUG] Routes imported successfully")

# ==================== التصدير ====================
__all__ = [
    'suppliers_auth_bp',
    'PasswordHasher',
    'CSRFProtector',
]
