# -*- coding: utf-8 -*-
from flask import Blueprint

# تعريف الـ Blueprint للمحفظة
supplier_wallet_bp = Blueprint(
    'supplier_wallet',
    __name__,
    template_folder='templates',
    url_prefix='/supplier/wallet'
)

# المتغيرات المطلوبة للتسجيل الديناميكي في النظام
MODULE_NAME = 'الإدارة المالية والمحفظة'
ICON = 'fas fa-wallet'
SHOW_IN_SUPPLIER = True

# تعريف الروابط بالهيكل الذي يتوقعه النظام الديناميكي (قائمة من القواميس أو القواميس المباشرة حسب نظام مشروعك)
MENU_ITEMS = [
    {'endpoint': 'supplier_wallet.dashboard', 'title': 'لوحة المحفظة', 'icon': 'fas fa-chart-pie'},
    {'endpoint': 'supplier_wallet.transactions', 'title': 'سجل الحركات', 'icon': 'fas fa-exchange-alt'},
    {'endpoint': 'supplier_wallet.withdraw', 'title': 'طلب سحب أرباح', 'icon': 'fas fa-money-bill-wave'}
]

def register_module(app):
    app.register_blueprint(supplier_wallet_bp)
