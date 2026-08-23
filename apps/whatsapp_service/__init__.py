# coding: utf-8
# 📂 apps/whatsapp_service/__init__.py

"""
WhatsApp Service Package for Mahjoub Online
-------------------------------------------
تغليف حزمة خدمة الواتساب وتوفير الوصول المباشر للـ Blueprint والمكونات الرئيسية.
"""

from apps.whatsapp_service.routes import whatsapp_bp

__all__ = ['whatsapp_bp']
