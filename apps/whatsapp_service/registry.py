# coding: utf-8
# 📂 apps/whatsapp_service/registry.py

from flask import Flask
# نفترض أنك قمت بتعريف whatsapp_bp في ملف __init__.py داخل مجلد routes
from .routes import whatsapp_bp

MODULE_NAME = "خدمة الواتساب"
MODULE_ICON = "fa-brands fa-whatsapp"
SHOW_IN_SUPPLIER = False  # إبقاء الصلاحية للإدارة فقط

# روابط القائمة الجانبية التي ستظهر تلقائياً
NAV_ITEMS = [
    {"endpoint": "whatsapp.chat_dashboard", "title": "المحادثات المباشرة"},
    {"endpoint": "whatsapp.logs_dashboard", "title": "سجل الرسائل"},
    {"endpoint": "whatsapp.settings_dashboard", "title": "إعدادات الربط"}
]

def register_module(app: Flask):
    """
    تسجيل موديول الواتساب تحت المسار المحمي /admin/whatsapp
    """
    app.register_blueprint(whatsapp_bp, url_prefix='/admin/whatsapp')
