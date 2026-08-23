# -*- coding: utf-8 -*-
# 📂 apps/whatsapp_service/registry.py

MODULE_NAME = "خدمة الواتساب"
MODULE_ICON = "bi-whatsapp"
SHOW_IN_ADMIN = True

# روابط الموديول التي ستظهر في القائمة الجانبية لوحة التحكم
LINKS = {
    'whatsapp_service.index': 'إدارة مراسلات الواتساب'
}

def register_module(app):
    from apps.whatsapp_service.routes import whatsapp_bp
    
    if 'whatsapp_bp' not in app.blueprints:
        app.register_blueprint(whatsapp_bp, url_prefix# -*- coding: utf-8 -*-
# 📂 apps/whatsapp_service/registry.py

MODULE_NAME = "خدمة الواتساب"
MODULE_ICON = "bi-whatsapp"
SHOW_IN_ADMIN = True

# روابط الموديول التي ستظهر في القائمة الجانبية لوحة التحكم
LINKS = {
    'whatsapp_service.index': 'إدارة مراسلات الواتساب'
}

def register_module(app):
    try:
        # محاولة استيراد الـ Blueprint من ملف whatsapp_api الموجود لديك
        from apps.whatsapp_service.whatsapp_api import whatsapp_bp
        
        if 'whatsapp_bp' not in app.blueprints:
            app.register_blueprint(whatsapp_bp, url_prefix='/admin/whatsapp')
    except ImportError as e:
        print(فشل تسجيل موديول الواتساب لعدم توفر الـ Blueprint في whatsapp_api.py: {e})='/admin/whatsapp')
