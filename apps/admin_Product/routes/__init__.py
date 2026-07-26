# coding: utf-8
# 📂 apps/admin_Product/routes/__init__.py

from flask import Blueprint

# إنشاء Blueprint الرئيسي
admin_product_bp = Blueprint('admin_product_bp', __name__, template_folder='templates')

# ✅ استيراد كل ملف على حدة
from .sync import *
from .reviews import *
from .crud import *
from .stats import *
from .products import *

__all__ = ['admin_product_bp']
