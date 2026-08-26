# apps/whatsapp_service/__init__.py
"""
سوق محجوب أونلاين - حزمة خدمة الواتساب ومحرك الذكاء الاصطناعي
WhatsApp Service Package for Meta Cloud API v26.0
"""

from .service import WhatsAppService
from .routes import whatsapp_bp
from .registry import register_service, register_module

__all__ = [
    "WhatsAppService",
    "whatsapp_bp",
    "register_service",
    "register_module"
]
