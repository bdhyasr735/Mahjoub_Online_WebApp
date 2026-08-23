# coding: utf-8
# 📂 apps/whatsapp/registry.py

from flask import Flask
from .routes import whatsapp_bp

# ⚙️ إعدادات واجهة الموديول
MODULE_NAME = "بوابة الواتساب"
MODULE_ICON = "fa-brands fa-whatsapp"  # أيقونة الواتساب
SHOW_IN_SUPPLIER = False  # إبقاء الموديول خاصاً بالإدارة فقط (لوحة تحكم الإدارة)

# 🔗 الروابط التي ستظهر في القائمة الجانبية
NAV_ITEMS = [
    {
        "endpoint": "whatsapp_admin.index", 
        "title": "إدارة الرسائل"
    }
]

def register_module(app: Flask):
    """
    تسجيل الـ Blueprint الخاص بالواتساب في التطبيق الرئيسي.
    """
    app.register_blueprint(whatsapp_bp, url_prefix='/admin/whatsapp')
