# coding: utf-8
# 📂 apps/whatsapp_service/registry.py

from apps.whatsapp_service.routes import whatsapp_bp

MODULE_NAME = "خدمة الواتساب"
MODULE_ICON = "fab fa-whatsapp text-amber-400"

# الروابط التي ستظهر تلقائياً في القائمة الجانبية (تأكد أن أسماء الـ endpoints تطابق ما لديك)
LINKS = {
    'whatsapp.dashboard': 'لوحة التحكم',
    'whatsapp.logs': 'سجل الرسائل',
    'whatsapp.settings': 'إعدادات الربط'
}

def register_module(app):
    """
    تسجيل Blueprint الواتساب وتحديد بادئة المسار (URL Prefix)
    """
    if 'whatsapp' not in app.blueprints:
        app.register_blueprint(whatsapp_bp, url_prefix='/whatsapp')
