# 📂 apps/admin_suppliers_list/registry.py

MODULE_NAME = "إدارة الموردين"
MODULE_ICON = "fas fa-users"

LINKS = {
    "suppliers_bp.list_suppliers": "قائمة الشركاء",
    "admin_suppliers_add_bp.add_supplier_or_staff": "تعميد شريك جديد",
    "admin_suppliers_wallets.suppliers_wallets_controller.index": "إدارة محافظ الموردين" # ⬅️ إضافة الرابط الجديد
}

def register_module(app):
    try:
        from apps.admin_suppliers_list.routes import suppliers_bp
        from apps.admin_suppliers_add.routes import admin_suppliers_add_bp
        from apps.admin_suppliers_wallets.routes import suppliers_wallets_controller # ⬅️ استيراد المتحكم الخاص بك
        
        app.register_blueprint(suppliers_bp, url_prefix='/admin/suppliers')
        app.register_blueprint(admin_suppliers_add_bp, url_prefix='/admin/suppliers_add')
        app.register_blueprint(suppliers_wallets_controller.bp, url_prefix='/admin/suppliers-wallets') # ⬅️ تسجيل الموديول
        
        print("✅ [Registry]: تم تسجيل موديول الموردين والمحافظ بنجاح.")
    except Exception as e:
        print(f"❌ [Registry Error]: {e}")
