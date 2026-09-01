# -*- coding: utf-8 -*-

MODULE_NAME = "الإدارة المالية"
ICON = "fas fa-wallet"

MENU_ITEMS = {
    'supplier_wallet.wallet_dashboard_redirect': 'حركة المحفظة',
    'supplier_wallet.withdraw': 'سحب الرصيد'
}

def register_module(app):
    """دالة التسجيل الديناميكي المطلوبة من النظام لتفعيل الموديول"""
    # يمكن وضع أي إعدادات خاصة بالتسجيل هنا إن وجدت، أو تركها لتسجيل الموديول بنجاح
    return True
