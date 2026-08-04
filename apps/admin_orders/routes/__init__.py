# coding: utf-8
# 📂 apps/admin_orders/routes/__init__.py

from flask import Blueprint

# 1. ⚠️ يجب تعريف الـ Blueprint أولاً وقبل أي استيراد للملفات الفرعية
admin_orders_bp = Blueprint(
    'admin_orders', 
    __name__, 
    template_folder='../templates', 
    url_prefix='/admin/orders'
)

# 2. الآن فقط قم باستيراد الملفات الفرعية (orders و actions) لكي تتمكن من رؤية الـ Blueprint وتسجيل نفسها بأمان
from apps.admin_orders.routes import orders, actions
