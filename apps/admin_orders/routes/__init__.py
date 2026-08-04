# coding: utf-8
# 📂 apps/admin_orders/routes/__init__.py

import os
from flask import Blueprint

# المسار المطلق لمجلد القوالب
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates')

# إنشاء Blueprint الرئيسي لطلبات الأدمن
admin_orders_bp = Blueprint(
    'admin_orders_bp', 
    __name__, 
    template_folder=template_dir
)

# 1. استيراد ملف العروض والصفحات الأساسية
from . import orders

# 2. استيراد ملف العمليات والـ AJAX الخلفية (لكي يتم تسجيل مسارات الـ decorators تلقائياً)
from . import actions

# 3. استيراد دالة التسجيل واستدعائها إن وجدت في orders.py
if hasattr(orders, 'register_admin_orders_route'):
    orders.register_admin_orders_route(admin_orders_bp)

__all__ = ['admin_orders_bp']
