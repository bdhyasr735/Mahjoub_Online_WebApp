# coding: utf-8
# 📂 apps/suppliers_permissions/registry.py

from apps.suppliers_permissions.routes import suppliers_permissions_bp

# إعدادات تعريف الموديول للنظام الديناميكي
MODULE_NAME = "إدارة الصلاحيات"
MODULE_ICON = "fa-user-shield"  # أيقونة احترافية تناسب الصلاحيات والموظفين

# تحديد روابط التنقل الخاصة بالموديول والتي تظهر في القائمة الجانبية
LINKS = [
    {
        "title": "صلاحيات الموظفين",
        "url": "/permissions",  # المسار التابع للـ Blueprint
        "icon": "fa-users-cog"
    }
]

# الإعداد الحاسم: تفعيل ظهور هذا الموديول داخل لوحة الموردين بدلاً من لوحة الإدارة العامة
SHOW_IN_SUPPLIER = True

def register_module(app):
    """
    دالة تسجيل الموديول المربوطة بمحرك النظام التلقائي في apps/__init__.py
    """
    # تسجيل الـ Blueprint مع بادئة مسار واضحة ومنظمة للموردين
    app.register_blueprint(suppliers_permissions_bp, url_prefix='/supplier')
