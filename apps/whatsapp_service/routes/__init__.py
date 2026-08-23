# coding: utf-8
# 📂 apps/whatsapp_service/routes/__init__.py

from flask import Blueprint

whatsapp_bp = Blueprint(
    'whatsapp_service',
    __name__,
    template_folder='../templates',
    static_folder='../static'
)

# استيراد ملفات المسارات الداخلية لتفعيل الـ Routes
from apps.whatsapp_service.routes import views, api
