# -*- coding: utf-8 -*-
# 📂 apps/admin_treasury/__init__.py
"""
ملف تهيئة وبناء البلوبرنت لموديول الرقابة المالية (الخزينة المركزية) وحسابات الضمان
مشروع Mahjoub Online WebApp
"""

from flask import Blueprint

# 1. تعريف البلوبرنت أولاً وقبل كل شيء ليكون متاحاً للاستيراد
admin_treasury_bp = Blueprint(
    'admin_treasury',
    __name__,
    template_folder='templates',
    static_folder='static'
)

# 2. استيراد المتحكمات لتسجيل المسارات (داخل try-except لتفادي الأخطاء المبكرة)
try:
    from apps.admin_treasury.routes import treasury_controller
except ImportError as e:
    pass
