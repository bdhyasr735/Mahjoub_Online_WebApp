# coding: utf-8
# 📂 apps/supplier_wallet/__init__.py
"""
حزمة محفظة المورد ومنظومة الحركات المالية
Mahjoub Online WebApp
"""

from flask import Blueprint

# 1. إنشاء الـ Blueprint الموحد للمورد
supplier_wallet_bp = Blueprint(
    'supplier_wallet',
    __name__,
    template_folder='templates',
    static_folder='static'
)

# 2. استيراد المسارات مباشرة لتسجيلها على الـ Blueprint
from apps.supplier_wallet.routes import wallet_routes
