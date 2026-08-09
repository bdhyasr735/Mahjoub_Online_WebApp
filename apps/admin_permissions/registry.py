# -*- coding: utf-8 -*-
# 📂 apps/admin_permissions/registry.py

# هذه التعريفات ضرورية لمنع الخطأ الذي واجهته (Module Registry Requirement)
MODULE_NAME = "إدارة الصلاحيات"
MODULE_ICON = "bi-shield-lock"
SHOW_IN_ADMIN = True

# قواميس الصلاحيات
ADMIN_PERMISSIONS_REGISTRY = {
    'manage_products': 'إدارة المنتجات وتعديلها',
    'manage_orders': 'إدارة ومتابعة الطلبات',
    'manage_suppliers': 'إدارة الموردين والمتاجر',
    'manage_treasury': 'الرقابة المالية والخزينة',
    'manage_staff': 'إدارة الموظفين والصلاحيات',
    'view_reports': 'عرض التقارير والإحصائيات'
}

SUPPLIER_PERMISSIONS_REGISTRY = {
    'supplier_manage_products': 'إدارة منتجات المتجر',
    'supplier_manage_orders': 'إدارة طلبات الزبائن',
    'supplier_manage_wallet': 'إدارة محفظة المورد',
    'supplier_manage_staff': 'إدارة موظفي المتجر'
}

# دالة التسجيل الأساسية للموديول
def register_module(app):
    from apps.admin_permissions.routes import admin_permissions_bp
    
    # التأكد من عدم تكرار التسجيل
    if 'admin_permissions_bp' not in app.blueprints:
        app.register_blueprint(admin_permissions_bp, url_prefix='/admin/permissions')
