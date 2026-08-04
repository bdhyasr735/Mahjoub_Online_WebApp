# coding: utf-8
# 📂 apps/admin_orders/routes/__init__.py

from flask import Blueprint

# تعريف الـ Blueprint الخاص بإدارة الطلبات مع تحديد مسارات القوالب والمجلدات الثابتة
admin_orders_bp = Blueprint(
    'admin_orders_bp',
    __name__,
    template_folder='../templates',
    static_folder='../static'
)

# استيراد ملفات المسارات الفرعية (مثل العرض والإجراءات والتحكم) 
# لضمان تسجيل كافة الروابط والـ decorators تلقائياً ضمن الـ Blueprint
from apps.admin_orders.routes import orders, actions
