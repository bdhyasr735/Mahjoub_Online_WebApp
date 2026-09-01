# -*- coding: utf-8 -*-
from flask import url_for

MODULE_NAME = "الإدارة المالية"
ICON = "fas fa-wallet"

# تعريف الروابط بحيث تتطابق مع أسماء الدوال في الـ routes.py
MENU_ITEMS = {
    'supplier_wallet.wallet_dashboard_redirect': 'حركة المحفظة',
    'supplier_wallet.withdraw': 'سحب الرصيد'
}
