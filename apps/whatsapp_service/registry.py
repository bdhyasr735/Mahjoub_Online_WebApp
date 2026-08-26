# -*- coding: utf-8 -*-
"""
سوق محجوب أونلاين - وحدة تسجيل الخدمة والتصاريح
Service Registry & Permissions Module for Mahgoob Online WhatsApp Service
Meta Cloud API v26.0 Edition
"""

import importlib
import logging

logger = logging.getLogger(__name__)

MODULE_NAME = "خدمة مراسلات واتساب"
DISPLAY_NAME = "خدمة مراسلات واتساب سوق محجوب أونلاين"
ICON = "fab fa-whatsapp"
SHOW_IN_SUPPLIER = True

# عناصر التنقل في القائمة الجانبية للوحة التحكم الرئيسية
NAV_ITEMS = [
    {
        "title": "لوحة المحادثات المباشرة",
        "endpoint": "/admin/whatsapp/dashboard",
        "icon": "fas fa-comments",
        "permission": "whatsapp.view_chat"
    },
    {
        "title": "قوالب ميتا المعتمدة",
        "endpoint": "/admin/whatsapp/templates",
        "icon": "fas fa-layer-group",
        "permission": "whatsapp.manage_templates"
    },
    {
        "title": "سجل الويب هوك (Live)",
        "endpoint": "/admin/whatsapp/webhook-logs",
        "icon": "fas fa-stream",
        "permission": "whatsapp.view_logs"
    },
    {
        "title": "إعدادات Meta Cloud API v26.0",
        "endpoint": "/admin/whatsapp/settings",
        "icon": "fas fa-cogs",
        "permission": "whatsapp.admin_settings"
    }
]

LINKS_DICT = {
    "/admin/whatsapp/dashboard": "لوحة المحادثات المباشرة",
    "/admin/whatsapp/templates": "قوالب ميتا المعتمدة",
    "/admin/whatsapp/webhook-logs": "سجل تدفق الويب هوك",
    "/admin/whatsapp/settings": "إعدادات وتوكنات Meta API"
}

# بيانات وصف الخدمة ونظام الصلاحيات والأمان
SERVICE_METADATA = {
    "name": "whatsapp_service",
    "display_name": DISPLAY_NAME,
    "version": "2.6.0",
    "api_version": "v26.0",
    "author": "Mahgoob Online Dev Team",
    "description": "تكامل سحابي مباشر مع Meta WhatsApp Cloud API v26.0 لإدارة محادثات العملاء والتجار، قوالب الإشعارات، وربط الذكاء الاصطناعي التلقائي (Gemini AI).",
    "icon": ICON,
    "links": LINKS_DICT,
    "admin_menu": NAV_ITEMS,
    "permissions": [
        "whatsapp.view_chat",
        "whatsapp.send_message",
        "whatsapp.manage_templates",
        "whatsapp.view_logs",
        "whatsapp.admin_settings"
    ],
    "webhook_endpoints": {
        "verification": "/api/whatsapp/webhook (GET)",
        "incoming_events": "/api/whatsapp/webhook (POST)"
    }
}

def register_service(app):
    """
    تسجيل Blueprint خدمة الواتساب تلقائياً في تطبيق Flask / Django الرئيسي
    """
    try:
        whatsapp_routes = importlib.import_module("apps.whatsapp_service.routes")
        
        # البحث عن Blueprint المعرف باسم whatsapp_bp أو whatsapp_service
        bp = getattr(whatsapp_routes, 'whatsapp_bp', None) or getattr(whatsapp_routes, 'whatsapp_service', None)
        
        if bp:
            if bp.name not in app.blueprints:
                app.register_blueprint(bp)
                app.logger.info("✅ [WhatsApp Service] Blueprint registered successfully with Meta Cloud API v26.0 routes.")
            else:
                app.logger.info("ℹ️ [WhatsApp Service] Blueprint is already registered in app.")
        else:
            app.logger.error("❌ [WhatsApp Service] No blueprint found in apps.whatsapp_service.routes.")
    except Exception as e:
        app.logger.error(f"❌ [WhatsApp Service] Failed to register blueprint: {e}")

    # تسجيل الميتا داتا في التطبيق العام
    if not hasattr(app, 'registered_services'):
        app.registered_services = {}
    app.registered_services['whatsapp_service'] = SERVICE_METADATA
    
    if not hasattr(app, 'registered_modules'):
        app.registered_modules = {}
    app.registered_modules['whatsapp_service'] = SERVICE_METADATA
    
    app.logger.info("✅ [WhatsApp Service] Metadata & permissions registered for Mahgoob Online.")

def register_module(app):
    register_service(app)
