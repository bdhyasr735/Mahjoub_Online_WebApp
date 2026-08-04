# coding: utf-8
# 📂 apps/admin_orders/__init__.py

"""
موديول إدارة الطلبات - يجمع الـ Blueprints ويصدرها للتطبيق.
"""

from .routes import admin_orders_bp, actions_bp

__all__ = ['admin_orders_bp', 'actions_bp']
