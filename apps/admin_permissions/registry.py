# apps/admin_permissions/registry.py
from flask import Blueprint
from .routes import admin_permissions_bp

MODULE_NAME = "إدارة الصلاحيات"
MODULE_ICON = "fas fa-shield-alt"
LINKS = {
    'قائمة الأدوار': 'admin_permissions.roles_list',
    'إسناد الصلاحيات': 'admin_permissions.assign_permissions'
}
SHOW_IN_SUPPLIER = False

def register_module(app):
    app.register_blueprint(admin_permissions_bp)
