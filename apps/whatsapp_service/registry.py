# -*- coding: utf-8 -*-
# 📂 apps/whatsapp_service/registry.py

MODULE_NAME = "خدمة الواتساب"
MODULE_ICON = "fas fa-comments"
SHOW_IN_ADMIN = True

# توفير كلا الصيغتين (النصية المباشرة والـ Endpoint) لضمان التقاطها أياً كانت الطريقة التي يقرأ بها القالب
LINKS = {
    'whatsapp_service.chat_dashboard': 'إدارة مراسلات الواتساب',
    '/admin/whatsapp/dashboard': 'إدارة مراسلات الواتساب'
}

def get_admin_links():
    """دالة مساعدة احتياطية في حال كانت لوحة التحكم تبحث عن دالة جلب الروابط مباشرة"""
    return [
        {"endpoint": "whatsapp_service.chat_dashboard", "label": "إدارة مراسلات الواتساب"}
    ]

def register_module(app):
    from apps.whatsapp_service.routes import whatsapp_bp
    
    if 'whatsapp_service' not in app.blueprints:
        app.register_blueprint(whatsapp_bp, url_prefix='/admin/whatsapp')
