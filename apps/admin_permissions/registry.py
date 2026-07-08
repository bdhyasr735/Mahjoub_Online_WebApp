# coding: utf-8
# 📂 apps/admin_permissions/registry.py

from .routes import admin_permissions_bp

# إعدادات الموديول للظهور في القائمة الجانبية
MODULE_NAME = "إدارة الصلاحيات"
MODULE_ICON = "fas fa-shield-alt"

# الروابط التي ستظهر في القائمة المنسدلة
LINKS = {
    'قائمة الأدوار': 'admin_permissions.roles_list',
    'إسناد الصلاحيات': 'admin_permissions.assign_permissions'
}

# تحديد هل يظهر للمورد أم للمدير فقط
SHOW_IN_SUPPLIER = False

def register_module(app):
    """تسجيل الـ Blueprint الخاص بالموديول في التطبيق."""
    app.register_blueprint(admin_permissions_bp)
