# coding: utf-8
# 📂 apps/whatsapp_service/__init__.py

"""
WhatsApp Service Module for Mahgoob Online (محجوب أونلاين)
===========================================================
Modular Flask Blueprint integrating Meta WhatsApp Cloud API v21.0
"""

from .routes import whatsapp_bp
from .registry import register_service

def init_app(app):
    """Initializes the WhatsApp service module with Flask app."""
    app.register_blueprint(whatsapp_bp)
    register_service(app)

__all__ = ['whatsapp_bp', 'init_app']
