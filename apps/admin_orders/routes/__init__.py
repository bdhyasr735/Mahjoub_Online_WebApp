# coding: utf-8
# 📂 apps/admin_orders/__init__.py

import os
from flask import Blueprint

# تحديد المسارات المطلقة للقوالب والمجلدات الثابتة
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

# تعريف الـ Blueprint الرئيسي للموديول
admin_orders_bp = Blueprint(
    'admin_orders_bp',
    __name__,
    template_folder=template_dir,
    static_folder=static_dir
)

# استيراد المسارات لتسجيل الروابط
from apps.admin_orders.routes import orders, actions
