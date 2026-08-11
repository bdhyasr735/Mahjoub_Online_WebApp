# -*- coding: utf-8 -*-
# 📂 apps/admin_product/__init__.py

from flask import Blueprint

# تعريف الـ Blueprint الخاص بإدارة المنتجات ومتجر محجوب أونلاين
admin_product_bp = Blueprint(
    'admin_product',
    __name__,
    template_folder='templates',
    static_folder='static'
)

# استيراد المسارات لضمان تسجيلها داخل الـ Blueprint
from . import routes
