# coding: utf-8
# 📂 apps/supplier_wallet/__init__.py

from flask import Blueprint

# 1. إنشاء الـ Blueprint أولاً
supplier_wallet_bp = Blueprint(
    'supplier_wallet',
    __name__,
    template_folder='templates',
    static_folder='static'
)

# 2. استيراد المسارات بعد إنشاء الـ Blueprint
from . import routes
