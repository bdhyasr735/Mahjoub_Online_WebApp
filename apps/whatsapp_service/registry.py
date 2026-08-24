# -*- coding: utf-8 -*-
"""
Service Registry & Permissions Module for Mahgoob Online
"""

MODULE_NAME = "خدمة مراسلات واتساب"
DISPLAY_NAME = "خدمة مراسلات واتساب محجوب أونلاين"
ICON = "fab fa-whatsapp"
SHOW_IN_SUPPLIER = False

NAV_ITEMS = [
    {
        "title": "محادثات العملاء",
        "endpoint": "whatsapp_service.chat_dashboard"
    },
    {
        "title": "سجل الرسائل",
        "endpoint": "whatsapp_service.logs_dashboard"
    },
    {
        "title": "إعدادات Meta Cloud API",
        "endpoint": "whatsapp_service.settings_dashboard"
    }
]

SERVICE_METADATA = {
    "name": "whatsapp_service",
    "display_name": DISPLAY_NAME,
    "version": "1.2.0",
    "author": "Mahgoob Online Dev Team",
    "description": "تكامل سحابي مباشر مع Meta WhatsApp Cloud API v21.0 لإدارة محادثات العملاء، قوالب الإشعارات، وربط الطلبات ORD-#",
    "icon": ICON,
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
    """التسجيل التقليدي للخدمة"""
    if not hasattr(app, 'registered_services'):
        app.registered_services = {}
    app.registered_services['whatsapp_service'] = SERVICE_METADATA

def register_module(app):
    """الدالة الأساسية التي يبحث عنها النظام الديناميكي في apps/__init__.py"""
    register_service(app)
    print("✅ [Mahgoob WhatsApp Service] Registered successfully via dynamic engine.")
