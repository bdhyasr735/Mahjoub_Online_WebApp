# -*- coding: utf-8 -*-
# 📂 apps/admin_treasury/__init__.py
"""
ملف تهيئة وبناء البلوبرنت لموديول الرقابة المالية (الخزينة المركزية) وحسابات الضمان
مشروع Mahjoub Online WebApp
"""

# استورد الـ Blueprint من مكانه الحقيقي (من داخل مجلد routes)
from .routes.treasury_controller import admin_treasury_bp

# أخبر بايثون أن هذا هو المتغير العمومي للمجلد
__all__ = ["admin_treasury_bp"]
