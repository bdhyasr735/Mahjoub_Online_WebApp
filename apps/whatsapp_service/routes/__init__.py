# 📂 apps/whatsapp_service/routes/__init__.py
from flask import Blueprint

# 1. إنشاء الـ Blueprint بالاسم المطابق لـ registry.py
whatsapp_bp = Blueprint('whatsapp_service', __name__)

# 2. استيراد ملفات المسارات الداخلية لتسجيلها (عدّل أسماء الملفات حسب ما لديك)
from . import dashboard, logs, settings
