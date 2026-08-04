# coding: utf-8
# 📂 apps/admin_orders/__init__.py

from flask import Blueprint

admin_orders_bp = Blueprint(
    'admin_orders_bp',
    __name__,
    template_folder='templates',
    static_folder='static'
)

# استيراد المسارات لتسجيلها تلقائياً مع الـ Blueprint
from apps.admin_orders.routes import orders, actions
