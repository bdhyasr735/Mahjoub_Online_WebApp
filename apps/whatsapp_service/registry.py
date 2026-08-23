# -*- coding: utf-8 -*-
# 📂 apps/whatsapp_service/registry.py

MODULE_NAME = "خدمة الواتساب"
MODULE_ICON = "fas fa-comments"
SHOW_IN_ADMIN = True

# الروابط الكاملة لشمل لوحة التحكم، المحادثات، السجلات، والإعدادات
LINKS = {
    'whatsapp_service.dashboard': 'لوحة التحكم الرئيسية',
    'whatsapp_service.chat_view': 'مراسلات الواتساب المباشرة',
    'whatsapp_service.logs_view': 'سجلات النظام',
    'whatsapp_service.settings_view': 'إعدادات الواتساب'
}

def get_admin_links():
    """دالة مساعدة لإرجاع كافة روابط الخدمة لوحة التحكم الإدارية"""
    return [
        {"endpoint": "whatsapp_service.dashboard", "label": "لوحة التحكم الرئيسية"},
        {"endpoint": "whatsapp_service.chat_view", "label": "مراسلات الواتساب المباشرة"},
        {"endpoint": "whatsapp_service.logs_view", "label": "سجلات النظام"},
        {"endpoint": "whatsapp_service.settings_view", "label": "إعدادات الواتساب"}
    ]

def register_module(app):
    from apps.whatsapp_service.routes import whatsapp_bp
    
    if 'whatsapp_service' not in app.blueprints:
        app.register_blueprint(whatsapp_bp, url_prefix='/admin/whatsapp')
