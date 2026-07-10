# coding: utf-8
# 📂 apps/suppliers_permissions/registry.py

from apps.suppliers_permissions.routes import suppliers_permissions_bp

# إعدادات تعريف الموديول للنظام الديناميكي
MODULE_NAME = "إدارة الصلاحيات"
MODULE_ICON = "fa-user-shield"

# ✨ الإصلاح الجوهري: جعل المفتاح هو الـ Endpoint والقيمة هي تفاصيل الرابط ليتوافق مع السطر 44 في base.html
LINKS = {
    "suppliers_permissions.permissions": {
        "title": "صلاحيات الموظفين",
        "url": "/permissions",
        "icon": "fa-users-cog"
    }
}

# تفعيل ظهور هذا الموديول داخل لوحة الموردين
SHOW_IN_SUPPLIER = True

def register_module(app):
    """
    دالة تسجيل الموديول المربوطة بمحرك النظام التلقائي
    """
    app.register_blueprint(suppliers_permissions_bp, url_prefix='/supplier')
