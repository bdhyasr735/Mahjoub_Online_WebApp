# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/__init__.py

from flask import Blueprint

# 1. تعريف الـ Blueprint أولاً وقبل كل شيء
supplier_wallet_bp = Blueprint(
    'supplier_wallet',
    __name__,
    template_folder='templates',
    static_folder='static'
)

# 2. استيراد المسارات في نهاية الملف (بعد إنشاء الـ Blueprint تماماً لمنع الاستيراد الدائري)
try:
    from apps.supplier_wallet.routes import wallet_routes
except Exception as e:
    print(f"⚠️ [Wallet Init Error]: تعذر استيراد مسارات المورد: {e}")
