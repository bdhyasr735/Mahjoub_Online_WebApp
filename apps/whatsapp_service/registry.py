# coding: utf-8
# 📂 apps/whatsapp_service/registry.py

from apps.whatsapp_service.routes import whatsapp_bp

MODULE_NAME = "خدمة الواتساب"
MODULE_ICON = "fab fa-whatsapp text-emerald-400"

# الروابط والأزرار التي ستظهر في القائمة الجانبية
LINKS = {
    'whatsapp.dashboard': 'لوحة التحكم والمحادثات',
    'whatsapp.logs': 'سجل الرسائل',
    'whatsapp.settings': 'إعدادات الربط'
}

def register_module(app):
    """
    تسجيل Blueprint الواتساب وتحديد بادئة المسار
    """
    if 'whatsapp' not in app.blueprints:
        app.register_blueprint(whatsapp_bp, url_prefix='/whatsapp')
