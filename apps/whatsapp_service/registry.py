# coding: utf-8
# 📂 apps/whatsapp_service/registry.py

MODULE_NAME = "خدمة الواتساب"
MODULE_ICON = "fa-brands fa-whatsapp"
SHOW_IN_SUPPLIER = False

# صيغة Tuples متوافقة تماماً مع item[0] و item[1] في admin_base.html
NAV_ITEMS = [
    ("whatsapp.chat_dashboard", "المحادثات المباشرة"),
    ("whatsapp.logs_dashboard", "سجل الرسائل"),
    ("whatsapp.settings_dashboard", "إعدادات Meta API"),
]

def register_module(app):
    """تسجيل الـ Blueprint وإعفاء المسارات من CSRF"""
    from apps.whatsapp_service.routes import whatsapp_bp
    from apps.extensions import csrf

    if whatsapp_bp.name not in app.blueprints:
        app.register_blueprint(whatsapp_bp, url_prefix='/admin/whatsapp')
        csrf.exempt(whatsapp_bp)
