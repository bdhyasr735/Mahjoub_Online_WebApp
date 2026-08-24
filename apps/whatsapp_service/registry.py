# -*- coding: utf-8 -*-
"""
Service Registry & Permissions Module for Mahgoob Online
"""

import importlib

MODULE_NAME = "خدمة مراسلات واتساب"
DISPLAY_NAME = "خدمة مراسلات واتساب محجوب أونلاين"
ICON = "fab fa-whatsapp"
SHOW_IN_SUPPLIER = False

# استخدام المسارات المباشرة التي يتوقعها محرك القوائم الجانبية لديك
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

# قاموس الروابط المتوافق مع محرك admin_base.html والقائمة الجانبية
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

def register_module(app):
    """الدالة الأساسية لتسجيل الـ Blueprint والخدمة ديناميكياً في تطبيق Flask"""
    
    # 1. تسجيل الـ Blueprint مع تحديد url_prefix ليطابق المسارات (/whatsapp)
    try:
        whatsapp_routes = importlib.import_module("apps.whatsapp.routes")
        if hasattr(whatsapp_routes, 'whatsapp_bp'):
            # التأكد من عدم تسجيل الـ Blueprint مسبقاً لمنع حدوث تكرار
            blueprint_names = [bp.name for bp in app.blueprints.values()]
            if 'whatsapp' not in blueprint_names:
                app.register_blueprint(whatsapp_routes.whatsapp_bp, url_prefix='/whatsapp')
                print("✅ [Mahgoob WhatsApp Service] Blueprint registered successfully at /whatsapp.")
    except Exception as e:
        print(f"❌ [Mahgoob WhatsApp Service] Failed to register blueprint: {e}")

    # 2. تسجيل البيانات الوصفية والقوائم لكي يقرأها النظام الديناميكي
    if not hasattr(app, 'registered_services'):
        app.registered_services = {}
    app.registered_services['whatsapp_service'] = SERVICE_METADATA
    
    if not hasattr(app, 'registered_modules'):
        app.registered_modules = {}
    app.registered_modules['whatsapp_service'] = SERVICE_METADATA
    
    print("✅ [Mahgoob WhatsApp Service] Registered successfully via dynamic engine.")
