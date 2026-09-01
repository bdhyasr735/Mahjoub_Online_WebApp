# -*- coding: utf-8 -*-
from flask import Blueprint

supplier_wallet_bp = Blueprint(
    'supplier_wallet',
    __name__,
    template_folder='templates',
    url_prefix='/supplier/wallet'
)

MODULE_NAME = 'الإدارة المالية'
ICON = 'fas fa-wallet'
SHOW_IN_SUPPLIER = True

# الروابط الأساسية لتظهر النصوص العربية بدقة عند النزول أو الضغط
LINKS = {
    'supplier_wallet.wallet_dashboard_redirect': 'لوحة المحفظة',
    'supplier_wallet.transactions': 'سجل الحركات المالية',
    'supplier_wallet.withdraw': 'طلب سحب الرصيد'
}

MENU_ITEMS = [
    {
        'endpoint': 'supplier_wallet.wallet_dashboard_redirect',
        'title': 'لوحة المحفظة',
        'name': 'لوحة المحفظة',
        'icon': 'fas fa-chart-pie'
    },
    {
        'endpoint': 'supplier_wallet.transactions',
        'title': 'سجل الحركات المالية',
        'name': 'سجل الحركات المالية',
        'icon': 'fas fa-exchange-alt'
    },
    {
        'endpoint': 'supplier_wallet.withdraw',
        'title': 'طلب سحب الرصيد',
        'name': 'طلب سحب الرصيد',
        'icon': 'fas fa-money-bill-wave'
    }
]

def register_module(app):
    app.register_blueprint(supplier_wallet_bp)
