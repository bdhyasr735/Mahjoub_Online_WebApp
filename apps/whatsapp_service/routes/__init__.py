# -*- coding: utf-8 -*-
# 📂 apps/whatsapp_service/routes/__init__.py

from flask import Blueprint

# تعريف الـ Blueprint الخاص بخدمة الواتساب
whatsapp_bp = Blueprint(
    'whatsapp_service',
    __name__,
    template_folder='templates',
    static_folder='static'
)

# استيراد ملفات المسارات لكي يتم تسجيلها وتفعيلها مع الـ Blueprint
from . import dashboard, api, actions, webhook
