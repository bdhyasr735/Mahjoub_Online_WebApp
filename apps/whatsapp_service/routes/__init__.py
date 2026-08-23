# coding: utf-8
# 📂 apps/whatsapp_service/routes/__init__.py

"""
مجلد مسارات خدمة الواتساب (WhatsApp Service Routes)
يتم هنا تعريف الـ Blueprint الرئيسي واستيراد وحدات المسارات الفرعية.
"""

from flask import Blueprint

# 1. إنشاء الـ Blueprint الخاص بخدمة الواتساب
whatsapp_bp = Blueprint(
    'whatsapp_service',
    __name__,
    template_folder='../templates'
)

# 2. استيراد وحدات المسارات (Routes) لربطها بالـ Blueprint
# ملاحظة: تم وضع الاستيراد هنا أسفل إنشاء whatsapp_bp لمنع الدوران الدائري (Circular Imports)
from . import dashboard

# إذا كانت لديك ملفات مسارات فرعية أخرى للسجلات والإعدادات، يمكنك تفعيل استيرادها هنا:
# from . import logs
# from . import settings
