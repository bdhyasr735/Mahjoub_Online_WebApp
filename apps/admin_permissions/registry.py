# -*- coding: utf-8 -*-
"""
اسم الموديول: إدارة الصلاحيات ورتب المستخدمين
الوصف: موديول مستقل لإدارة صلاحيات موظفي الإدارة، الموردين، وموظفي الموردين منصة محجوب أونلاين.
"""

MODULE_NAME = "إدارة الصلاحيات"
MODULE_ICON = "fa-shield-alt"
MODULE_DESCRIPTION = "التحكم الكامل والجامع لصلاحيات موظفي الإدارة والموردين وكوادرهم"
MODULE_VERSION = "1.0.0"
MODULE_ORDER = 5
MODULE_ENABLED = True

def register_module(app):
    """
    دالة تسجيل الموديول تلقائياً في تطبيق Flask عند الإقلاع عبر Dynamic Factory System
    """
    from apps.admin_permissions.routes import permissions_bp
    
    # تسجيل الـ Blueprint داخل تطبيق Flask
    app.register_blueprint(permissions_bp, url_prefix="/admin/permissions")
    
    # تسجيل الموديول في القائمة العامة بالتطبيق إذا كانت موجودة
    if not hasattr(app, "registered_modules"):
        app.registered_modules = {}
        
    app.registered_modules["admin_permissions"] = {
        "name": MODULE_NAME,
        "icon": MODULE_ICON,
        "description": MODULE_DESCRIPTION,
        "version": MODULE_VERSION,
        "endpoint": "admin_permissions.index"
    }