# coding: utf-8
# 📂 apps/supplier_wallet/__init__.py
"""
حزمة محفظة المورد ومنظومة الحركات المالية
Mahjoub Online WebApp
"""

from flask import Blueprint

# 1. إنشاء الـ Blueprint الرئيسي للمورد أولاً
supplier_wallet_bp = Blueprint(
    'supplier_wallet',
    __name__,
    template_folder='templates',
    static_folder='static',
    url_prefix='/supplier/wallet'
)

# 2. استيراد المسارات في نهاية الملف حصراً لمنع حدوث الاستيراد الدائري (Circular Import)
from apps.supplier_wallet.routes import wallet_routes, admin_routes
