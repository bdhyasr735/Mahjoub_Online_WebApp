# -*- coding: utf-8 -*-
# 📂 apps/whatsapp_service/routes/__init__.py

from flask import Blueprint

# 1. إنشاء الـ Blueprint الخاص بخدمة الواتساب
whatsapp_bp = Blueprint(
    'whatsapp_service',
    __name__,
    template_folder='../templates',
    static_folder='../static'
)

# 2. استيراد ملفات المسارات الفعلية فقط في نهاية الملف لتجنب الاستيراد الدائري
from . import dashboard, api, actions, webhook
