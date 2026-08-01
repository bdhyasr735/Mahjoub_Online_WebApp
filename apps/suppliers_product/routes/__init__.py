# coding: utf-8
# 📂 apps/suppliers_product/routes/__init__.py

import os
from flask import Blueprint

# ✅ المسار المطلق لمجلد القوالب
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates')

# إنشاء Blueprint الرئيسي للمورد
suppliers_product_bp = Blueprint(
    'suppliers_product_bp', 
    __name__, 
    template_folder=template_dir
)

# ✅ استيراد جميع الـ Routes الخاصة بالمورد
from . import sync
from . import reviews
from . import stats
from . import products

__all__ = ['suppliers_product_bp']
