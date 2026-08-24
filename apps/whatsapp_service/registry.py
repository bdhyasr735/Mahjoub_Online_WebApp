# -*- coding: utf-8 -*-
"""
Service Registry & Permissions Module for Mahgoob Online
"""

MODULE_NAME = "خدمة مراسلات واتساب"
DISPLAY_NAME = "خدمة مراسلات واتساب محجوب أونلاين"
ICON = "fab fa-whatsapp"
SHOW_IN_SUPPLIER = False

# هيكل الروابط المتوافق تماماً مع حلقة القالب الديناميكي links في admin_base.html
LINKS_DICT = {
    "whatsapp_service.chat_dashboard": "محادثات العملاء",
    "whatsapp_service.logs_dashboard": "سجل الرسائل",
    "whatsapp_service.settings_dashboard": "إعدادات Meta Cloud API"
}

SERVICE_METADATA = {
    "name": "whatsapp_service",
    "display_name": DISPLAY_NAME,
    "version": "1.2.0",
    "author": "Mahgoob Online Dev Team",
    "description": "تكامل سحابي مباشر مع Meta WhatsApp Cloud API v21.0 لإدارة محادثات العملاء، قوالب الإشعارات، وربط الطلبات ORD-#",
    "icon": ICON,
    "links": LINKS_DICT,  # هذا المفتاح الذي يقرأه admin_base.html مباشرة
    "admin_menu": LINKS_DICT,
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
    
    # للتأكد من توافق المحرك الديناميكي إذا كان يبحث عن registered_modules
    if not hasattr(app, 'registered_modules'):
        app.registered_modules = {}
    app.registered_modules['whatsapp_service'] = SERVICE_METADATA

def register_module(app):
    """الدالة الأساسية التي يبحث عنها النظام الديناميكي في apps/__init__.py"""
    register_service(app)
    print("✅ [Mahgoob WhatsApp Service] Registered successfully via dynamic engine.")
