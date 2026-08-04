# coding: utf-8
# 📂 apps/admin_orders/routes/__init__.py

from flask import Blueprint

# تعريف الـ Blueprint الخاص بإدارة الطلبات
admin_orders_bp = Blueprint(
    'admin_orders_bp',
    __name__,
    template_folder='../templates',
    static_folder='../static'
)

# استيراد ملفات المسارات لتسجيل الروابط والـ decorators تلقائياً
from apps.admin_orders.routes import orders, actions
