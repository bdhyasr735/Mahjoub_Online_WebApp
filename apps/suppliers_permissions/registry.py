# -*- coding: utf-8 -*-
# 📂 apps/suppliers_permissions/registry.py

"""
سجل الصلاحيات المتاحة لموظفي الموردين والمساعدين في منصة محجوب أونلاين
mahjoub.online Supplier Permissions Registry
"""

MODULE_NAME = "إدارة الصلاحيات"
MODULE_ICON = "bi-shield-lock"
SHOW_IN_SUPPLIER = True

LINKS = {
    'suppliers_permissions_bp.index': '🛡️ إدارة صلاحيات الموظفين'
}

def register_module(app):
    # تم تعديل المسار هنا ليطابق اسم المجلد الحقيقي 'suppliers_permissions'
    from apps.suppliers_permissions.routes import suppliers_permissions_bp
    
    if 'suppliers_permissions_bp' not in app.blueprints:
        app.register_blueprint(suppliers_permissions_bp, url_prefix='/supplier/permissions')
        print("✅ [Registry]: تم تسجيل موديول 'suppliers_permissions' بنجاح.")
    else:
        print("ℹ️ [Registry]: موديول 'suppliers_permissions' مسجل مسبقاً.")

# بقية الكود كما هو تماماً (SUPPLIER_PERMISSIONS_REGISTRY, إلخ)
