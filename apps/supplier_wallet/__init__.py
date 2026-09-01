# -*- coding: utf-8 -*-
"""
📂 apps/supplier_wallet/__init__.py
حزمة موديول محفظة المورد (Supplier Wallet Package)
"""

from apps.supplier_wallet.registry import supplier_wallet_bp, MODULE_NAME, ICON, LINKS, MENU_ITEMS

# استيراد المسارات لضمان تسجيل الـ Routes المرتبطة بالـ Blueprint
from apps.supplier_wallet import routes

__all__ = [
    'supplier_wallet_bp',
    'MODULE_NAME',
    'ICON',
    'LINKS',
    'MENU_ITEMS'
]
