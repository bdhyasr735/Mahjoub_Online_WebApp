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

# ✅ استيراد ملفات العمليات والمراجعة ومنتجات الموردين لتسجيل الـ Routes تلقائياً
from . import crud
from . import reviews
from . import products

__all__ = ['suppliers_product_bp']
