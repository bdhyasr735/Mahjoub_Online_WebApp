# -*- coding: utf-8 -*-
"""
📂 apps/supplier_wallet/__init__.py
ملف تهيئة موديول محفظة المورد (Supplier Wallet Module Initialization)
"""

from apps.supplier_wallet.registry import MODULE_NAME, ICON, SHOW_IN_SUPPLIER, MENU_ITEMS
from apps.supplier_wallet.routes import wallet_bp

def register_module(app):
    """
    دالة التسجيل الديناميكي المطلوبة من النظام لتفعيل موديول محفظة المورد
    وتسجيل البلوبرنت الخاص به داخل تطبيق الفلاسك الرئيسي.
    """
    app.register_blueprint(wallet_bp)
    return True
