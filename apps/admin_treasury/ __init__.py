# -*- coding: utf-8 -*-
# 📂 apps/admin_treasury/__init__.py
"""
ملف تهيئة وبناء البلوبرنت لموديول الرقابة المالية (الخزينة المركزية) وحسابات الضمان
مشروع Mahjoub Online WebApp
"""

from flask import Blueprint

# تعريف البلوبرنت بشكل مباشر وصحيح ليتم استيراده بسلاسة
admin_treasury_bp = Blueprint(
    'admin_treasury',
    __name__,
    template_folder='templates',
    static_folder='static'
)

# استيراد المتحكمات لتفعيل المسارات
try:
    from apps.admin_treasury.routes import treasury_controller
except ImportError as e:
    print(f"[!] Warning: Could not import treasury controllers: {e}")
