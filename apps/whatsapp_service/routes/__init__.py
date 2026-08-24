# -*- coding: utf-8 -*-
# 📂 apps/whatsapp_service/routes/__init__.py

from flask import Blueprint

# تعريف الـ Blueprint الخاص بخدمة الواتساب
whatsapp_bp = Blueprint(
    'whatsapp_service',
    __name__,
    template_folder='../templates',
    static_folder='../static'
)

# استيراد المسارات (Routes) هنا في الأسفل بعد إنشاء الـ Blueprint تماماً لتجنب الاستيراد الدائري
from . import dashboard, api
