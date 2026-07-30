# coding: utf-8
# 📂 apps/admin_Product/routes/__init__.py

import os
from flask import Blueprint

# ✅ المسار المطلق لمجلد القوالب
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates')

# إنشاء Blueprint الرئيسي (تمت إزالة إعدادات static_folder و static_url_path لأنها لم تعد مستخدمة)
admin_product_bp = Blueprint(
    'admin_product_bp', 
    __name__, 
    template_folder=template_dir
)

# ✅ استيراد جميع الـ Routes
from . import sync
from . import reviews
from . import crud
from . import stats

# ✅ استيراد products.py وتسجيل الـ Route
from .products import register_products_route
register_products_route(admin_product_bp)

__all__ = ['admin_product_bp']
