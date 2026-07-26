# coding: utf-8
# 📂 apps/admin_Product/routes/__init__.py

from flask import Blueprint

# إنشاء Blueprint الرئيسي
admin_product_bp = Blueprint('admin_product_bp', __name__, template_folder='templates')

# استيراد جميع الـ Routes
from . import sync
from . import reviews
from . import crud
from . import stats

# ✅ استيراد products.py بشكل مختلف
import importlib
products_module = importlib.import_module('.products', package='apps.admin_Product.routes')

__all__ = ['admin_product_bp']
