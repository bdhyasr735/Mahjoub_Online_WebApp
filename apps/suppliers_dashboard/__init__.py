# -*- coding: utf-8 -*-
# 📂 apps/suppliers_dashboard/__init__.py

from apps.suppliers_dashboard.registry import suppliers_dashboard_bp, init_app

# تصدير الـ Blueprint ودالة التسجيل لتكون جاهزة للاستدعاء في التطبيق الرئيسي
__all__ = ['suppliers_dashboard_bp', 'init_app']
