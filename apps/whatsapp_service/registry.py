# coding: utf-8
# 📂 apps/whatsapp_service/registry.py

from flask import current_app

MODULE_NAME = 'مركز الواتساب'
MODULE_ICON = 'fa-brands fa-whatsapp'
SHOW_IN_SUPPLIER = False

NAV_ITEMS = [
    {
        'endpoint': 'whatsapp_service.chat_dashboard',
        'title': 'صندوق الرسائل',
        'icon': 'fa-solid fa-comments'
    },
    {
        'endpoint': 'whatsapp_service.logs_dashboard',
        'title': 'سجل الرسائل',
        'icon': 'fa-solid fa-list-check'
    },
    {
        'endpoint': 'whatsapp_service.settings_dashboard',
        'title': 'إعدادات الربط',
        'icon': 'fa-solid fa-gear'
    }
]

# البيانات الوصفية للخدمة (تُستخدم في النظام الرئيسي)
SERVICE_METADATA = {
    "name": "whatsapp_service",
    "display_name": MODULE_NAME,
    "icon": MODULE_ICON,
    "version": "1.2.0",
    "author": "Mahgoob Online Dev Team",
    "description": "تكامل سحابي مباشر مع Meta WhatsApp Cloud API لإدارة محادثات العملاء، قوالب الإشعارات، وربط الطلبات",
    "admin_menu": NAV_ITEMS,
    "permissions": [
        "whatsapp.view_chat",
        "whatsapp.send_message",
        "whatsapp.view_logs",
        "whatsapp.admin_settings"
    ]
}

# قائمة الروابط (لتوافق مع نظام القوائم الديناميكي)
LINKS = {
    item["endpoint"]: item["title"] 
    for item in NAV_ITEMS
}

def register_module(app):
    """
    تسجيل موديول الواتساب ومساراته تلقائياً في التطبيق الرئيسي
    """
    try:
        from .routes import whatsapp_bp
        
        # تسجيل الـ Blueprint إذا لم يكن مسجلاً من قبل
        if 'whatsapp_service' not in app.blueprints:
            app.register_blueprint(whatsapp_bp, url_prefix='/admin/whatsapp')
            print("✅ [WhatsApp Registry]: تم تسجيل Blueprint 'whatsapp_service' بنجاح.")
        
        # تسجيل البيانات الوصفية للخدمة في التطبيق
        if not hasattr(app, 'registered_services'):
            app.registered_services = {}
        app.registered_services['whatsapp_service'] = SERVICE_METADATA
        
        # إنشاء جداول قاعدة البيانات (اختياري)
        with app.app_context():
            try:
                from apps.models.whatsapp_models import WhatsAppMessageLog, WhatsAppWebhookEvent, WhatsAppCustomerContact
                from apps.extensions import db
                db.create_all()
                print("✅ [WhatsApp Registry]: تم التحقق من إنشاء جداول قاعدة البيانات بنجاح.")
            except Exception as db_err:
                print(f"⚠️ [WhatsApp Registry]: خطأ في إنشاء الجداول: {db_err}")
        
        print(f"✅ [WhatsApp Registry]: تم تسجيل موديول '{MODULE_NAME}' بنجاح.")
        
    except Exception as e:
        print(f"❌ [WhatsApp Registry]: فشل تسجيل الموديول: {e}")
