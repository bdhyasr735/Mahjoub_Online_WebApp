# coding: utf-8
# 📂 apps/suppliers_orders/routes/__init__.py

import os
from flask import Blueprint  # ✅ هذا السطر كان مفقوداً

# المسار المطلق لمجلد القوالب
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates')

# إنشاء Blueprint الرئيسي للطلبات (مورد)
suppliers_orders_bp = Blueprint(
    'suppliers_orders_bp', 
    __name__, 
    template_folder=template_dir
)

# استيراد جميع الـ Routes الخاصة بطلبات المورد
from . import orders

# استيراد دالة التسجيل واستدعائها
from .orders import register_orders_route
register_orders_route(suppliers_orders_bp)

__all__ = ['suppliers_orders_bp']
