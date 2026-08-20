# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/__init__.py

from flask import Blueprint

# 1. تعريف الـ Blueprint الأساسي
supplier_wallet_bp = Blueprint(
    'supplier_wallet',
    __name__,
    template_folder='templates',
    static_folder='static'
)

# 2. استيراد المتحكم (الـ routes) مباشرة بناءً على مكان وجوده الفعلي
try:
    from apps.supplier_wallet import wallet_routes
except Exception as e:
    print(f"⚠️ [Wallet Init Error]: تعذر استيراد مسارات المورد: {e}")
