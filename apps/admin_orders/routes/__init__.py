# coding: utf-8
# 📂 apps/admin_orders/routes/__init__.py

from flask import Blueprint

# استيراد الـ Blueprints من الملفات الفرعية
from .orders import admin_orders_bp
from .actions import actions_bp

# تصدير الـ Blueprints لتسجيلها في التطبيق الرئيسي (apps/__init__.py)
__all__ = ['admin_orders_bp', 'actions_bp']
