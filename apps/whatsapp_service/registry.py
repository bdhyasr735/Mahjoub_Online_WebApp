# coding: utf-8
# 📂 apps/whatsapp_service/registry.py

from apps.whatsapp_service.routes import whatsapp_bp

MODULE_NAME = "خدمة الواتساب"
MODULE_ICON = "fab fa-whatsapp text-amber-400"
SHOW_IN_SUPPLIER = False

NAV_ITEMS = [
    {"endpoint": "whatsapp.dashboard", "title": "لوحة التحكم"},
    {"endpoint": "whatsapp.logs", "title": "سجل الرسائل"},
    {"endpoint": "whatsapp.settings", "title": "إعدادات الربط"}
]

def register_module(app):
    """تسجيل الـ Blueprint الخاص بخدمة الواتساب تلقائياً"""
    if 'whatsapp' not in app.blueprints:
        app.register_blueprint(whatsapp_bp, url_prefix='/whatsapp')
