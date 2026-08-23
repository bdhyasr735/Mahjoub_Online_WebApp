
# coding: utf-8
# 📂 apps/whatsapp_service/__init__.py

from flask import Blueprint

# تعريف البلوبرنت الأساسي للخدمة (يتم استخدامه وتسجيله ديناميكياً عبر registry.py)
whatsapp_bp = Blueprint(
    'whatsapp_service',
    __name__,
    template_folder='templates',
    static_folder='static'
)

# استيراد المسارات والملفات التابعة للموديول لضمان تسجيل الروابط عند تحميله
from apps.whatsapp_service import routes
