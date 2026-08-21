"""
WhatsApp Service Package Initialization
"""

from .registry import register_module, SERVICE_METADATA
from .routes.whatsapp_controller import whatsapp_bp

__all__ = ['register_module', 'SERVICE_METADATA', 'whatsapp_bp']
