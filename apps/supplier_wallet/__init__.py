# -*- coding: utf-8 -*-
"""
📂 apps/supplier_wallet/__init__.py
"""
from apps.supplier_wallet.registry import supplier_wallet_bp, MODULE_NAME, MODULE_ICON, LINKS, register_module
from apps.supplier_wallet import routes

__all__ = [
    'supplier_wallet_bp',
    'MODULE_NAME',
    'MODULE_ICON',
    'LINKS',
    'register_module'
]
