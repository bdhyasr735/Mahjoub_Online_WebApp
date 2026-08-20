# coding: utf-8
# 📂 apps/supplier_wallet/routes/__init__.py
"""
حزمة المسارات (Routes) الخاصة بموديول محفظة المورد
يتم من خلالها تجميع مسارات لوحة المورد والإدارة
"""

# استيراد ملفات المسارات لضمان تسجيلها وتفعيلها عند استدعاء المجلد
try:
    from . import wallet_routes
except ImportError as e:
    print(f"⚠️ [Wallet Routes Init]: تعذر استيراد wallet_routes: {e}")

try:
    from . import admin_routes
except ImportError as e:
    # قد لا يكون ملف admin_routes موجوداً أو مستخدماً في كل الموديولات
    pass

__all__ = ['wallet_routes', 'admin_routes']
