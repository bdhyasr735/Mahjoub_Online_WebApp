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

# الروابط بصيغتها المزدوجة لضمان توافقها مع أي قالب عرض (قاموس أو قائمة)
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
    """تسجيل الـ Blueprint وإضافة الموديول للسجل العام ليقرأه القالب الجانبي"""
    app.register_blueprint(supplier_wallet_bp)
    
    # تسجيل الموديول في السجل العام للتطبيق إذا كان مدعوماً
    if not hasattr(app, 'supplier_modules'):
        app.supplier_modules = {}
        
    app.supplier_modules['supplier_wallet'] = {
        'name': MODULE_NAME,
        'icon': ICON,
        'links': LINKS,
        'menu_items': MENU_ITEMS,
        'show_in_supplier': SHOW_IN_SUPPLIER
    }
