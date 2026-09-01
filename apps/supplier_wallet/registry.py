# -*- coding: utf-8 -*-
from flask import Blueprint

# تعريف الـ Blueprint للمحفظة
supplier_wallet_bp = Blueprint(
    'supplier_wallet',
    __name__,
    template_folder='templates',
    url_prefix='/supplier/wallet'
)

# بيانات القائمة الجانبية للمورد (لكي تظهر في الـ base.html)
MODULE_NAME = 'الإدارة المالية والمحفظة'
ICON = 'fas fa-wallet'
SHOW_IN_SUPPLIER = True

LINKS = {
    'supplier_wallet.dashboard': 'لوحة المحفظة',
    'supplier_wallet.transactions': 'سجل الحركات',
    'supplier_wallet.withdraw': 'طلب سحب أرباح'
}

def register_module(app):
    app.register_blueprint(supplier_wallet_bp)
