# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/registry.py

from apps.supplier_wallet.routes import wallet_bp

MODULE_NAME = "محفظة المورد"
DISPLAY_NAME = "المحفظة المالية"
MODULE_ICON = "fa-wallet"
IS_LAYOUT_CONTAINER = False
SHOW_IN_SUPPLIER = True

# الروابط الموجهة الآمنة التي لا تتطلب تمرير wallet_id يدوياً في القائمة
LINKS = {
    'supplier_wallet.wallet_dashboard_redirect': 'رصيد المحفظة',
    'supplier_wallet.transactions_redirect': 'سجل العمليات المالي',
    'supplier_wallet.withdraw_redirect': 'طلب سحب الرصيد'
}

MENU_ITEMS = [
    {'endpoint': 'supplier_wallet.wallet_dashboard_redirect', 'title': 'رصيد المحفظة', 'icon': 'fa-wallet'},
    {'endpoint': 'supplier_wallet.transactions_redirect', 'title': 'سجل العمليات المالي', 'icon': 'fa-list'},
    {'endpoint': 'supplier_wallet.withdraw_redirect', 'title': 'طلب سحب الرصيد', 'icon': 'fa-money-bill-wave'}
]

def register_module(app):
    if wallet_bp.name not in app.blueprints:
        app.register_blueprint(wallet_bp)
        print(f"✅ [Registry]: تم تسجيل {DISPLAY_NAME} بنجاح.")
