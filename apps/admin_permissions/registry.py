# -*- coding: utf-8 -*-
"""
ملف التسجيل الديناميكي لـ موديول الصلاحيات (Registry)
يتكامل تلقائياً مع دالة create_app ومصنع الموديولات.
"""

MODULE_NAME = "إدارة الصلاحيات"
MODULE_ICON = "fa-shield-alt"
MODULE_DESCRIPTION = "وحدة التحكم المستقلة لصلاحيات موظفي الإدارة، الموردين، وموظفيهم"
MODULE_VERSION = "1.0.0"
MODULE_ORDER = 5
MODULE_ENABLED = True

# الروابط الديناميكية التي ستظهر في القائمة الجانبية (Sidebar)
LINKS = {
    "admin_permissions.index": "عرض الصلاحيات"
}

def register_module(app):
    """
    تسجيل الـ Blueprint والموديول داخل تطبيق Flask الرئيسي تلقائياً
    """
    from apps.admin_permissions.routes import admin_permissions_bp
    
    # تسجيل البلوبرينت
    app.register_blueprint(admin_permissions_bp)
    
    # حصر الموديولات المسجلة في التطبيق
    if not hasattr(app, "registered_modules"):
        app.registered_modules = {}
        
    app.registered_modules["admin_permissions"] = {
        "name": MODULE_NAME,
        "icon": MODULE_ICON,
        "description": MODULE_DESCRIPTION,
        "version": MODULE_VERSION,
        "endpoint": "admin_permissions.index",
        "links": LINKS
    }
