# coding: utf-8
# 📂 apps/whatsapp_service/routes/__init__.py

import os
from flask import Blueprint

# تحديد المسار المطلق لمجلد templates الخاص بموديول الواتساب
# نرجع خطوة للخلف من مجلد routes للوصول لـ templates
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

whatsapp_bp = Blueprint(
    'whatsapp_service',
    __name__,
    template_folder=TEMPLATE_DIR
)

# استيراد المسارات
from . import dashboard
