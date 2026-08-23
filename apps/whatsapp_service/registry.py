# -*- coding: utf-8 -*-
# 📂 apps/whatsapp_service/registry.py

MODULE_NAME = "خدمة الواتساب"
MODULE_ICON = "fa-brands fa-whatsapp"
SHOW_IN_ADMIN = True

# الروابط بصيغة Dict لتتوافق مع نظام المحرك الداخلي
LINKS = {
    'whatsapp.chat_dashboard': 'المحادثات المباشرة',
    'whatsapp.logs_dashboard': 'سجل الرسائل',
    'whatsapp.settings_dashboard': 'إعدادات Meta API'
}

def register_module(app):
    from apps.whatsapp_service.routes import whatsapp_bp
    
    if 'whatsapp' not in app.blueprints and 'whatsapp_bp' not in app.blueprints:
        app.register_blueprint(whatsapp_bp, url_prefix='/admin/whatsapp')
