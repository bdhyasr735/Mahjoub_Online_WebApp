# coding: utf-8
# 📂 apps/admin_suppliers_list/registry.py

from .routes import suppliers_bp

MODULE_NAME = "إدارة الموردين" # اسم الموديول الموحد
MODULE_ICON = "fa-users"       # الأيقونة التي ستظهر للقسم

LINKS = {
    "إدارة الموردين": {
        "قائمة الشركاء": "suppliers_bp.list_suppliers" 
    }
}

def register_module(app):
    try:
        app.register_blueprint(suppliers_bp, url_prefix='/admin/suppliers')
        print("✅ [Registry]: تم تسجيل موديول 'admin_suppliers_list' بنجاح.")
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول 'admin_suppliers_list': {e}")
