# coding: utf-8
# 📂 apps/admin_orders/__init__.py

from .routes.orders import admin_orders_bp
from .routes.items_controller import items_bp

# إذا كان لديك ملف actions آخر، تأكد من وجوده أو استبدله بما يناسب مشروعك
try:
    from .routes.actions import actions_bp
except ImportError:
    actions_bp = None

__all__ = ['admin_orders_bp', 'items_bp', 'actions_bp']
