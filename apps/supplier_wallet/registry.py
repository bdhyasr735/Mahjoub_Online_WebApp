# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/registry.py

from apps.supplier_wallet.routes import wallet_bp

MODULE_NAME = "محفظة المورد"
DISPLAY_NAME = "المحفظة المالية"
MODULE_ICON = "fa-wallet"
IS_LAYOUT_CONTAINER = False

# ✅ تصحيح أسماء الـ Endpoints لتتوافق 100% مع مسارات wallet_bp المعرفة في routes.py
LINKS = {
    'supplier_wallet.wallet_dashboard_redirect': 'رصيد المحفظة',
    'supplier_wallet.transactions': 'سجل العمليات المالي',
    'supplier_wallet.withdraw': 'طلب سحب الرصيد'
}

def register_module(app):
    if wallet_bp.name not in app.blueprints:
        app.register_blueprint(wallet_bp)
        print(f"✅ [Registry]: تم تسجيل {DISPLAY_NAME} بنجاح.")
