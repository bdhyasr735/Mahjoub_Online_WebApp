# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/__init__.py

from flask import Blueprint

# 1. تعريف الـ Blueprint الخاص بمحفظة المورد
supplier_wallet_bp = Blueprint(
    'supplier_wallet',
    __name__,
    template_folder='templates',
    static_folder='static'
)

# 2. استيراد المسارات لضمان ربطها بالـ Blueprint
# ملاحظة: يجب أن تحتوي ملفات الـ routes على ديكورات مثل @supplier_wallet_bp.route
try:
    from apps.supplier_wallet import routes
except ImportError as e:
    print(f"⚠️ [Wallet Init]: تعذر استيراد المسارات: {e}")
