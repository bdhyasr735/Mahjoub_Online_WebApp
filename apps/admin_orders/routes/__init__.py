# coding: utf-8
# 📂 apps/admin_orders/routes/__init__.py

from flask import Blueprint

# تعريف الـ Blueprint الرئيسي للموديول
admin_orders_bp = Blueprint(
    'admin_orders_bp',
    __name__,
    template_folder='../templates',
    url_prefix='/admin/orders'
)

# استيراد ملفات routes بعد تعريف الـ Blueprint لتجنب circular import
from . import orders
# لا تستورد actions هنا إلا إذا كان ضرورياً
# from . import actions
