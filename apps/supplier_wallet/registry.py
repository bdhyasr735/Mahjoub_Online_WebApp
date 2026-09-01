# -*- coding: utf-8 -*-
"""
📂 apps/supplier_wallet/registry.py
تسجيل موديول محفظة المورد والقوائم التابعة له
"""

from flask import Blueprint

supplier_wallet_bp = Blueprint(
    'supplier_wallet',
    __name__,
    template_folder='templates',
    url_prefix='/supplier/wallet'
)

MODULE_NAME = 'الإدارة المالية والمحفظة'
ICON = 'fas fa-wallet'
SHOW_IN_SUPPLIER = True

# الصيغة الأولى: القاموس (إذا كان قالب القائمة الجانبية يعتمد على .items())
LINKS = {
    'supplier_wallet.wallet_dashboard_redirect': 'لوحة المحفظة الرئيسية',
    'supplier_wallet.transactions': 'سجل الحركات المالية',
    'supplier_wallet.withdraw': 'طلب سحب أرباح'
}

# الصيغة الثانية: القائمة (إذا كان قالب القائمة الجانبية يعتمد على التكرار بقائمة كائن)
MENU_ITEMS = [
    {
        'endpoint': 'supplier_wallet.wallet_dashboard_redirect',
        'title': 'لوحة المحفظة الرئيسية',
        'icon': 'fas fa-chart-pie'
    },
    {
        'endpoint': 'supplier_wallet.transactions',
        'title': 'سجل الحركات المالية',
        'icon': 'fas fa-exchange-alt'
    },
    {
        'endpoint': 'supplier_wallet.withdraw',
        'title': 'طلب سحب أرباح',
        'icon': 'fas fa-money-bill-wave'
    }
]

def register_module(app):
    app.register_blueprint(supplier_wallet_bp)
