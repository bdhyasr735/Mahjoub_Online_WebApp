# coding: utf-8
# 📂 apps/supplier_wallet/__init__.py

from .registry import supplier_wallet_bp, register_module
from .routes.admin_routes import admin_wallet_bp

__all__ = ['supplier_wallet_bp', 'admin_wallet_bp', 'register_module']
