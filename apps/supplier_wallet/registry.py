# -*- coding: utf-8 -*-

MODULE_NAME = "الإدارة المالية"
ICON = "fas fa-wallet"
SHOW_IN_SUPPLIER = True

MENU_ITEMS = {
    'supplier_wallet.wallet_dashboard_redirect': 'حركة المحفظة',
    'supplier_wallet.withdraw': 'سحب الرصيد'
}

def register_module(app):
    """دالة التسجيل الديناميكي المطلوبة من النظام لتفعيل الموديول"""
    return True
