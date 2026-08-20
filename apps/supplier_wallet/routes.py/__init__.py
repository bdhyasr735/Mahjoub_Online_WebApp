# coding: utf-8
# 📂 apps/supplier_wallet/routes/__init__.py

"""
حزمة مسارات موديول المحفظة (Supplier Wallet Routes Package)
- تقوم بتجميع مسارات الموردين ومسارات الإدارة وتصديرها تلقائياً.
"""

from .wallet_routes import supplier_wallet_bp
from .admin_routes import admin_wallet_bp

__all__ = ['supplier_wallet_bp', 'admin_wallet_bp']
