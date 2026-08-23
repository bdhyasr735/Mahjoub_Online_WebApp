# coding: utf-8
from apps.whatsapp.routes import whatsapp_bp  # تأكد أن هذا هو اسم ملف الـ routes والـ Blueprint لديك

MODULE_NAME = "خدمة الواتساب"
MODULE_ICON = "fab fa-whatsapp text-amber-400"

LINKS = {
    'whatsapp.chat_dashboard': 'المحادثات المباشرة',
    'whatsapp.logs_dashboard': 'سجل الرسائل',
    'whatsapp.settings_dashboard': 'إعدادات الربط'
}

def register_module(app):
    """
    تسجيل الـ Blueprint الخاص بالواتساب رسمياً في التطبيق
    ليتم التعرف على الـ Endpoints الخاصة به وإضافته للقائمة الجانبية تلقائياً
    """
    if not app.blueprints.get('whatsapp'):
        app.register_blueprint(whatsapp_bp, url_prefix='/whatsapp')
