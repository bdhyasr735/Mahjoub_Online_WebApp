# coding: utf-8
"""
مسارات ومتحكمات محفظة الموردين (Flask Route Blueprints)
"""

from apps.supplier_wallet.routes.wallet_routes import wallet_bp
from apps.supplier_wallet.routes.admin_routes import admin_wallet_bp

__all__ = ['wallet_bp', 'admin_wallet_bp']
