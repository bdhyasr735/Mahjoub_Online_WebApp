# coding: utf-8
# 📂 apps/admin_orders/routes/__init__.py

from .orders import admin_orders_bp
from .actions import actions_bp

__all__ = ['admin_orders_bp', 'actions_bp']
