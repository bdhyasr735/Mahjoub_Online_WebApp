# coding: utf-8
# 📂 apps/whatsapp_service/routes/__init__.py

"""
WhatsApp Service Routes Package
Initializes the Blueprint and loads all endpoint sub-modules.
"""

import os
from flask import Blueprint

# 1. تحديد مسار مجلد القوالب الخاص بموديول الواتساب
template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')

# 2. إنشاء الـ Blueprint الرئيسي
whatsapp_bp = Blueprint(
    'whatsapp',
    __name__,
    template_folder=template_dir
)

# 3. استيراد المسارات الفرعية باستخدام Relative Imports لضمان ربطها بالـ Blueprint بدون مشاكل Circular Import
from . import dashboard
from . import actions
from . import api
from . import webhook
