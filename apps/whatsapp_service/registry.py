# -*- coding: utf-8 -*-
# 📂 apps/whatsapp_service/registry.py

MODULE_NAME = "خدمة الواتساب"
MODULE_ICON = "bi-whatsapp"
SHOW_IN_ADMIN = True

# روابط الموديول التي ستظهر في القائمة الجانبية (متوافقة مع دالة chat_dashboard)
LINKS = {
    'whatsapp_service.chat_dashboard': 'إدارة مراسلات الواتساب'
}

def register_module(app):
    # استيراد الـ Blueprint من مجلد routes الفرعي
    from apps.whatsapp_service.routes import whatsapp_bp
    
    if 'whatsapp_service' not in app.blueprints:
        app.register_blueprint(whatsapp_bp, url_prefix='/admin/whatsapp')
