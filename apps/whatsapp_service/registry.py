# -*- coding: utf-8 -*-
# 📂 apps/whatsapp_service/registry.py

MODULE_NAME = "خدمة الواتساب"
MODULE_ICON = "fas fa-comments"
SHOW_IN_ADMIN = True

# الروابط المطابقة تماماً لأسماء الدوال في ملفات الـ Routes
LINKS = {
    'whatsapp_service.chat_dashboard': 'إدارة مراسلات الواتساب',
    'whatsapp_service.logs_dashboard': 'سجلات النظام',
    'whatsapp_service.settings_dashboard': 'إعدادات الواتساب'
}

def get_admin_links():
    """دالة مساعدة لإرجاع كافة روابط الخدمة للوحة التحكم الإدارية"""
    return [
        {"endpoint": "whatsapp_service.chat_dashboard", "label": "إدارة مراسلات الواتساب"},
        {"endpoint": "whatsapp_service.logs_dashboard", "label": "سجلات النظام"},
        {"endpoint": "whatsapp_service.settings_dashboard", "label": "إعدادات الواتساب"}
    ]

def register_module(app):
    from apps.whatsapp_service.routes import whatsapp_bp
    
    if 'whatsapp_service' not in app.blueprints:
        app.register_blueprint(whatsapp_bp, url_prefix='/admin/whatsapp')
