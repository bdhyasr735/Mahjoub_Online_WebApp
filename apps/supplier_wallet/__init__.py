# -*- coding: utf-8 -*-
"""
📂 apps/supplier_wallet/__init__.py
تهيئة حزمة محفظة المورد وتصدير المكونات الأساسية لنظام التسجيل الديناميكي
"""

from apps.supplier_wallet.registry import register_module, MODULE_NAME, ICON, MENU_ITEMS
from apps.supplier_wallet.routes import wallet_bp

__all__ = ['register_module', 'wallet_bp', 'MODULE_NAME', 'ICON', 'MENU_ITEMS']
