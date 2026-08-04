# coding: utf-8
# 📂 apps/admin_orders/routes/__init__.py

from flask import Blueprint

# تعريف الـ Blueprint الرئيسي لإدارة الطلبات
admin_orders_bp = Blueprint(
    'admin_orders', 
    __name__, 
    template_folder='../templates', 
    url_prefix='/admin/orders'
)

# استيراد ملفات المسارات الفرعية لتسجيلها وتفعيلها تلقائياً
from apps.admin_orders.routes import orders, actions
