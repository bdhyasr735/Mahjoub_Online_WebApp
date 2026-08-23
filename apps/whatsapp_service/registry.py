# coding: utf-8
from flask import Blueprint

MODULE_NAME = "خدمة الواتساب"
MODULE_ICON = "fas fa-comments"

# الروابط التي ستظهر في القائمة الجانبية المنسدلة
LINKS = {
    '/admin/whatsapp/': 'إدارة مراسلات الواتساب',
    '/admin/whatsapp/logs': 'سجلات النظام',
    '/admin/whatsapp/settings': 'إعدادات الواتساب'
}

def register_module(app):
    """تسجيل بلوبرنت الواتساب تلقائياً"""
    try:
        from apps.whatsapp_service.routes import whatsapp_bp
        if 'whatsapp_service' not in app.blueprints:
            app.register_blueprint(whatsapp_bp, url_prefix='/admin/whatsapp')
            # استثناء الـ CSRF إذا لزم الأمر للـ Webhooks
            from apps.extensions import db
            # يمكن إضافة الاستثناء في حال تطلب الأمر
    except Exception as e:
        print(f"⚠️ [WhatsApp Registry Error]: {e}")
