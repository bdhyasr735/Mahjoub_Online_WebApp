# -*- coding: utf-8 -*-
# 📂 apps/whatsapp_service/registry.py

MODULE_NAME = "خدمة الواتساب"
MODULE_ICON = "fas fa-comments"  # استخدمنا أيقونة تتوافق تماماً مع FontAwesome في القالب
SHOW_IN_ADMIN = True

# العودة إلى صيغة الـ Endpoint التي يتوقعها safe_url_for في القالب
LINKS = {
    'whatsapp_service.chat_dashboard': 'إدارة مراسلات الواتساب'
}

def register_module(app):
    from apps.whatsapp_service.routes import whatsapp_bp
    
    if 'whatsapp_service' not in app.blueprints:
        app.register_blueprint(whatsapp_bp, url_prefix='/admin/whatsapp')
