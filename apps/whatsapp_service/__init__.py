# coding: utf-8
# 📂 apps/whatsapp_service/__init__.py

from flask import Blueprint

# تعريف البلوبرنت الخاص بالخدمة وتحديد مسارات القوالب والملفات الثابتة
whatsapp_bp = Blueprint(
    'whatsapp_service',
    __name__,
    template_folder='templates',
    static_folder='static'
)

# استيراد مجلد/ملفات المسارات لتفعيل الـ Routes الخاصة بالموديول
from apps.whatsapp_service import routes
