# coding: utf-8
# 📂 apps/suppliers_product/routes/__init__.py

import os
from flask import Blueprint

# ✅ المسار المطلق لمجلد القوالب الخاص بالموردين
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates')

# إنشاء Blueprint الخاص بالموردين
suppliers_product_bp = Blueprint(
    'suppliers_product_bp', 
    __name__, 
    template_folder=template_dir
)

# ✅ استيراد ملفات العمليات والمراجعة الخاصة بالموردين
from . import crud
from . import reviews

# ✅ استيراد products.py وتسجيل الـ Route الخاص بجدول منتجات الموردين
from .products import register_supplier_products_route
register_supplier_products_route(suppliers_product_bp)

__all__ = ['suppliers_product_bp']
