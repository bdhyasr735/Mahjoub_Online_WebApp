# coding: utf-8
# 📂 apps/admin_Product/routes/__init__.py

import os
from flask import Blueprint

# ✅ المسار المطلق لمجلد القوالب والملفات الثابتة
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates')
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static')

# إنشاء Blueprint الرئيسي مع المسار المطلق للقوالب والملفات الثابتة
admin_product_bp = Blueprint(
    'admin_product_bp', 
    __name__, 
    template_folder=template_dir,
    static_folder=static_dir,
    static_url_path='static'
)

# ✅ استيراد الـ Routes التي تستخدم الديكوراتور المباشر
from . import reviews
from . import crud
from . import stats

# ✅ استيراد وتسيجل مسارات المنتجات
from .products import register_products_route
register_products_route(admin_product_bp)

# ✅ استيراد وتسيجل مسارات المزامنة
from .sync import register_sync_route
register_sync_route(admin_product_bp)

__all__ = ['admin_product_bp']
