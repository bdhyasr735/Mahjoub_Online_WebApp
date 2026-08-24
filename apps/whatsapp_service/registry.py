# -*- coding: utf-8 -*-
"""
Service Registry & Permissions Module for Mahgoob Online
"""

import importlib

MODULE_NAME = "خدمة مراسلات واتساب"
DISPLAY_NAME = "خدمة مراسلات واتساب محجوب أونلاين"
ICON = "fab fa-whatsapp"
SHOW_IN_SUPPLIER = False

NAV_ITEMS = [
    {"title": "محادثات العملاء", "endpoint": "/whatsapp/chat"},
    {"title": "إعدادات Meta Cloud API", "endpoint": "/whatsapp/settings"}
]

LINKS_DICT = {
    "/whatsapp/chat": "محادثات العملاء",
    "/whatsapp/settings": "إعدادات Meta Cloud API"
}

SERVICE_METADATA = {
    "name": "whatsapp_service",
    "display_name": DISPLAY_NAME,
    "version": "1.2.0",
    "author": "Mahgoob Online Dev Team",
    "description": "تكامل سحابي مباشر مع Meta WhatsApp Cloud API لإدارة محادثات العملاء، قوالب الإشعارات، وربط الطلبات",
    "icon": ICON,
    "links": LINKS_DICT,
    "admin_menu": NAV_ITEMS,
    "permissions": [
        "whatsapp.view_chat",
        "whatsapp.send_message",
        "whatsapp.manage_templates",
        "whatsapp.view_logs",
        "whatsapp.admin_settings"
    ]
}

def register_service(app):
    try:
        whatsapp_routes = importlib.import_module("apps.whatsapp_service.routes")
        if hasattr(whatsapp_routes, 'whatsapp_service'):
            bp = whatsapp_routes.whatsapp_service
            if bp.name not in app.blueprints:
                app.register_blueprint(bp, url_prefix='/whatsapp')
                app.logger.info("✅ [WhatsApp Service] Blueprint registered at /whatsapp.")
            else:
                app.logger.info("ℹ️ [WhatsApp Service] Blueprint already registered.")
        elif hasattr(whatsapp_routes, 'whatsapp_bp'):
            bp = whatsapp_routes.whatsapp_bp
            if bp.name not in app.blueprints:
                app.register_blueprint(bp, url_prefix='/whatsapp')
                app.logger.info("✅ [WhatsApp Service] Blueprint (legacy) registered at /whatsapp.")
            else:
                app.logger.info("ℹ️ [WhatsApp Service] Blueprint (legacy) already registered.")
        else:
            app.logger.error("❌ [WhatsApp Service] No blueprint found.")
    except Exception as e:
        app.logger.error(f"❌ [WhatsApp Service] Failed to register blueprint: {e}")

    if not hasattr(app, 'registered_services'):
        app.registered_services = {}
    app.registered_services['whatsapp_service'] = SERVICE_METADATA
    
    if not hasattr(app, 'registered_modules'):
        app.registered_modules = {}
    app.registered_modules['whatsapp_service'] = SERVICE_METADATA
    
    app.logger.info("✅ [WhatsApp Service] Metadata registered.")

def register_module(app):
    register_service(app)
