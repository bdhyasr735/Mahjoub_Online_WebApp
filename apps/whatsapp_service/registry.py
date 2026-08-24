"""
Service Registry & Permissions Module for Mahgoob Online
"""

SERVICE_METADATA = {
    "name": "whatsapp_service",
    "display_name": "خدمة مراسلات واتساب محجوب أونلاين",
    "version": "1.2.0",
    "author": "Mahgoob Online Dev Team",
    "description": "تكامل سحابي مباشر مع Meta WhatsApp Cloud API v21.0 لإدارة محادثات العملاء، قوالب الإشعارات، وربط الطلبات ORD-#",
    "icon": "fab fa-whatsapp",
    "admin_menu": [
        {
            "title": "محادثات العملاء",
            "endpoint": "whatsapp_service.chat_dashboard",
            "icon": "fas fa-comments",
            "badge": "unread_count"
        },
        {
            "title": "سجل الرسائل",
            "endpoint": "whatsapp_service.logs_dashboard",
            "icon": "fas fa-database"
        },
        {
            "title": "إعدادات Meta Cloud API",
            "endpoint": "whatsapp_service.settings_dashboard",
            "icon": "fas fa-cog"
        }
    ],
    "permissions": [
        "whatsapp.view_chat",
        "whatsapp.send_message",
        "whatsapp.manage_templates",
        "whatsapp.view_logs",
        "whatsapp.admin_settings"
    ]
}

def register_service(app):
    """Registers service metadata in the central app registry."""
    if not hasattr(app, 'registered_services'):
        app.registered_services = {}
    app.registered_services['whatsapp_service'] = SERVICE_METADATA
    app.logger.info("✅ [Mahgoob WhatsApp Service] Registered successfully.")
