# -*- coding: utf-8 -*-
# 📂 apps/whatsapp_service/registry.py

MODULE_NAME = "خدمة الواتساب"
MODULE_ICON = "bi-whatsapp"
SHOW_IN_ADMIN = True

# استخدام المسار المباشر ليتوافق مع شرط startswith('/') في القالب مباشرة
LINKS = {
    '/admin/whatsapp/dashboard': 'إدارة مراسلات الواتساب'
}

def register_module(app):
    from apps.whatsapp_service.routes import whatsapp_bp
    
    if 'whatsapp_service' not in app.blueprints:
        app.register_blueprint(whatsapp_bp, url_prefix='/admin/whatsapp')
