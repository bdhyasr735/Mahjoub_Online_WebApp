# -*- coding: utf-8 -*-
"""
Service Registry & Permissions Module for Mahgoob Online
"""

MODULE_NAME = "خدمة مراسلات واتساب"
DISPLAY_NAME = "خدمة مراسلات واتساب محجوب أونلاين"
ICON = "fab fa-whatsapp"
SHOW_IN_SUPPLIER = False

# تعديل المسارات لتكون مسارات مباشرة تبدأ بـ / لتجنب خطأ URL rule must start with a slash
NAV_ITEMS = [
    {
        "title": "محادثات العملاء",
        "endpoint": "/whatsapp/dashboard"
    },
    {
        "title": "سجل الرسائل",
        "endpoint": "/whatsapp/logs"
    },
    {
        "title": "إعدادات Meta Cloud API",
        "endpoint": "/whatsapp/settings"
    }
]

# قاموس الروابط المتوافق مع محرك admin_base.html
LINKS_DICT = {
    "/whatsapp/dashboard": "محادثات العملاء",
    "/whatsapp/logs": "سجل الرسائل",
    "/whatsapp/settings": "إعدادات Meta Cloud API"
}

SERVICE_METADATA = {
    "name": "whatsapp_service",
    "display_name": DISPLAY_NAME,
    "version": "1.2.0",
    "author": "Mahgoob Online Dev Team",
    "description": "تكامل سحابي مباشر مع Meta WhatsApp Cloud API v21.0 لإدارة محادثات العملاء، قوالب الإشعارات، وربط الطلبات ORD-#",
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
    """التسجيل التقليدي للخدمة"""
    if not hasattr(app, 'registered_services'):
        app.registered_services = {}
    app.registered_services['whatsapp_service'] = SERVICE_METADATA
    
    # مزامنة محرك الـ registered_modules الديناميكي لكي يلتقطه القالب بسلاسة
    if not hasattr(app, 'registered_modules'):
        app.registered_modules = {}
    app.registered_modules['whatsapp_service'] = SERVICE_METADATA

def register_module(app):
    """الدالة الأساسية التي يبحث عنها النظام الديناميكي في apps/__init__.py"""
    register_service(app)
    print("✅ [Mahgoob WhatsApp Service] Registered successfully via dynamic engine.")
