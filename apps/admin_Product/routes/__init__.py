# coding: utf-8
# 📂 apps/admin_Product/routes/__init__.py

from flask import Blueprint

# إنشاء Blueprint الرئيسي
admin_product_bp = Blueprint('admin_product_bp', __name__, template_folder='templates')

# استيراد جميع الـ Routes
from . import products
from . import sync
from . import reviews
from . import crud
from . import stats

__all__ = ['admin_product_bp']
