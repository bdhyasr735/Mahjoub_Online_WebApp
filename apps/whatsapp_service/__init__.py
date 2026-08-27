# -*- coding: utf-8 -*-
# apps/whatsapp_service/__init__.py
"""
سوق محجوب أونلاين - حزمة خدمة الواتساب ومحرك الذكاء الاصطناعي
WhatsApp Service Package for Meta Cloud API v26.0
"""

from .service import WhatsAppService
from .routes import whatsapp_bp
from .contacts_bulk import contacts_bulk_bp  # ✅ إضافة Blueprint جهات الاتصال
from .registry import register_service, register_module

__all__ = [
    "WhatsAppService",
    "whatsapp_bp",
    "contacts_bulk_bp",  # ✅ إضافة إلى القائمة العامة
    "register_service",
    "register_module"
]
