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

# استيراد الـ Routes
from . import orders

# استيراد دالة التسجيل واستدعائها
from .orders import register_admin_orders_route
register_admin_orders_route(admin_orders_bp)

__all__ = ['admin_orders_bp']
