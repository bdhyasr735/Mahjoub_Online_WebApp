# coding: utf-8
# 📂 apps/admin_orders/routes/__init__.py

from flask import Blueprint

# 1. تعريف الـ Blueprint أولاً وقبل كل شيء
admin_orders_bp = Blueprint(
    'admin_orders', 
    __name__, 
    template_folder='../templates', 
    url_prefix='/admin/orders'
)

# 2. ثم استيراد ملفات المسارات لكي تسجل نفسها على هذا الـ Blueprint بأمان
from apps.admin_orders.routes import orders, actions
