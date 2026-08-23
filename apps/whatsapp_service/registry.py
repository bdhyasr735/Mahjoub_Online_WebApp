# coding: utf-8
# 📂 apps/whatsapp_service/registry.py

"""
Service Registry & Permissions Module for WhatsApp Service
"""

SERVICE_METADATA = {
    "name": "whatsapp_service",
    "display_name": "خدمة مراسلات واتساب محجوب أونلاين",
    "version": "1.2.0",
    "author": "Mahgoob Online Dev Team",
    "description": "تكامل سحابي مباشر مع Meta WhatsApp Cloud API v21.0 لإدارة محادثات العملاء، قوالب الإشعارات، وربط الطلبات ORD-#",
    "icon": "fab fa-whatsapp",
    "admin_menu": {
        "/admin/whatsapp/chat": "محادثات العملاء",
        "/admin/whatsapp/logs": "سجل الرسائل",
        "/admin/whatsapp/settings": "إعدادات Meta Cloud API"
    },
    "permissions": [
        "whatsapp.view_chat",
        "whatsapp.send_message",
        "whatsapp.manage_templates",
        "whatsapp.view_logs",
        "whatsapp.admin_settings"
    ]
}

MODULE_NAME = SERVICE_METADATA["display_name"]
MODULE_ICON = SERVICE_METADATA["icon"]
SHOW_IN_SUPPLIER = False

# جعل الروابط متوافقة مع القالب الديناميكي
LINKS = SERVICE_METADATA["admin_menu"]
SERVICE_METADATA["links"] = LINKS

def register_module(app):
    """
    تسجيل موديول الواتساب ومساراته تلقائياً في التطبيق الرئيسي
    """
    try:
        from apps.whatsapp_service.dashboard import whatsapp_bp  # الاستيراد من dashboard.py بناءً على هيكلة ملفاتك
        
        if 'whatsapp_service' not in app.blueprints and 'whatsapp_bp' not in [bp.name for bp in app.blueprints.values()]:
            app.register_blueprint(whatsapp_bp, url_prefix='/admin/whatsapp')
        
        with app.app_context():
            try:
                from apps.models.whatsapp_models import WhatsAppMessageLog, WhatsAppWebhookEvent, WhatsAppCustomerContact
                from apps.extensions import db
                
                db.create_all()
            except Exception as db_err:
                print(f"⚠️ [WhatsApp DB Creation Warning]: {db_err}")

        if not hasattr(app, 'registered_services'):
            app.registered_services = {}
            
        app.registered_services['whatsapp_service'] = SERVICE_METADATA
        print("✅ [Module]: تم تسجيل 'whatsapp_service' ومساراته والجداول بنجاح.")
        
    except Exception as e:
        print(f"❌ [Module]: خطأ في تسجيل 'whatsapp_service': {e}")
