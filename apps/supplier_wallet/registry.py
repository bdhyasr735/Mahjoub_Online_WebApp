# -*- coding: utf-8 -*-
from apps.supplier_wallet.routes import supplier_wallet_bp

MODULE_NAME = "محفظة المورد"
MODULE_ICON = "fa-wallet"
SHOW_IN_SUPPLIER = True

NAV_ITEMS = [
    {
        'endpoint': 'supplier_wallet_bp.wallet_dashboard',
        'title': 'لوحة المحفظة والعمليات'
    },
    {
        'endpoint': 'supplier_wallet_bp.withdraw',
        'title': 'سحب الرصيد'
    }
]

def register_module(app):
    """دالة التسجيل الديناميكي لموديول المحفظة"""
    if 'supplier_wallet_bp' not in app.blueprints:
        app.register_blueprint(supplier_wallet_bp)
    print("🟢 [موديول محفظة المورد]: تم تسجيل البلوبرنت بنجاح تحت المسار /supplier/wallet")
