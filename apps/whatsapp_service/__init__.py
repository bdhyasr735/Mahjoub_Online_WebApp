# -*- coding: utf-8 -*-
"""
📂 apps/whatsapp_service/__init__.py
وحدة خدمة واتساب - تهيئة الـ Blueprint وتسجيل المسارات
"""

from flask import Blueprint

# تعريف الـ Blueprint الخاص بخدمة واتساب
# الاسم 'whatsapp_service' يجب أن يتطابق مع ما يستخدم في url_for
whatsapp_bp = Blueprint(
    'whatsapp_service',
    __name__,
    template_folder='templates',
    static_folder='static'
)

# استيراد المسارات (routes) لتسجيلها في الـ Blueprint
# هذا الاستيراد يجب أن يكون بعد تعريف الـ Blueprint لتجنب الـ Circular Import
from . import routes

# عند استيراد هذا الملف، سيتم تسجيل جميع المسارات المُعرّفة في routes.py
# كما سيتم تفعيل Context Processor الخاص بـ settings تلقائياً
