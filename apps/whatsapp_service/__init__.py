# -*- coding: utf-8 -*-
"""
📂 apps/whatsapp_service/__init__.py
وحدة خدمة واتساب - تهيئة الـ Blueprint وتسجيل المسارات
"""

from flask import Blueprint

whatsapp_bp = Blueprint(
    'whatsapp_service',
    __name__,
    template_folder='templates',
    static_folder='static'
)

from . import routes
