# coding: utf-8
# 📂 apps/supplier_wallet/registry.py

from flask import Blueprint

MODULE_NAME = "الإدارة المالية للمحفظة"
MODULE_ICON = "fa-wallet"
SHOW_IN_SUPPLIER = True  # ليظهر في بوابة الموردين

# تعريف الروابط التي ستظهر في السيردبار
NAV_ITEMS = [
    {
        "endpoint": "supplier_wallet.wallet_dashboard",
        "title": "المحفظة والسندات",
        "icon": "fa-file-invoice-dollar"
    },
    {
        "endpoint": "supplier_wallet.withdraw",
        "title": "طلب تسوية مالية",
        "icon": "fa-hand-holding-usd"
    }
]

def register_module(app):
    from apps.supplier_wallet.routes import wallet_bp
    app.register_blueprint(wallet_bp)
    print("✅ [Registry]: تم تسجيل موديول 'محفظة الموردين' (مع خيار التسوية) بنجاح.")
