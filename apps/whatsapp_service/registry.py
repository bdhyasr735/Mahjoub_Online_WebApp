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

# المتغيرات المطلوبة ليتعرف عليها نظام التسجيل الديناميكي بسلاسة
MODULE_NAME = SERVICE_METADATA["display_name"]
MODULE_ICON = SERVICE_METADATA["icon"]
SHOW_IN_SUPPLIER = False

# تحويل قائمة القنوات الإدارية إلى قاموس (Links) ليتوافق مع الفحص الديناميكي في القالب
LINKS = {
    item["endpoint"]: item["title"] 
    for item in SERVICE_METADATA.get("admin_menu", [])
}

# حقن الـ links داخل الـ Metadata ليتوافق مع ما يبحث عنه admin_base.html
SERVICE_METADATA["links"] = LINKS

def register_module(app):
    """
    تسجيل موديول الواتساب ومساراته تلقائياً في التطبيق الرئيسي
    """
    try:
        from apps.whatsapp_service.routes.whatsapp_controller import whatsapp_bp
        
        # تسجيل الـ Blueprint إذا لم يكن مسجلاً من قبل لتجنب التكرار
        if 'whatsapp_service' not in app.blueprints:
            app.register_blueprint(whatsapp_bp, url_prefix='/admin/whatsapp')
        
        # تسجيل بيانات الموديول والخدمة في التطبيق
        if not hasattr(app, 'registered_services'):
            app.registered_services = {}
            
        app.registered_services['whatsapp_service'] = SERVICE_METADATA
        print("✅ [Module]: تم تسجيل 'whatsapp_service' ومساراته بنجاح.")
        
    except Exception as e:
        print(f"❌ [Module]: خطأ في تسجيل 'whatsapp_service': {e}")
