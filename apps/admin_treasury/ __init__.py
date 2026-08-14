# -*- coding: utf-8 -*-
# 📂 apps/admin_treasury/__init__.py
"""
ملف تهيئة وبناء البلوبرنت لموديول الخزينة المركزية وحسابات الضمان
مشروع Mahjoub Online WebApp
"""

from flask import Blueprint

# إنشاء البلوبرنت الخاص بالخزينة المركزية مع تحديد مسار القوالب والمجلدات المشتركة
admin_treasury_bp = Blueprint(
    'admin_treasury',
    __name__,
    template_folder='templates',
    static_folder='static'
)

# استيراد المتحكمات لتسجيل المسارات المرتبطة بها داخل البلوبرنت
from apps.admin_treasury.routes import treasury_controller
