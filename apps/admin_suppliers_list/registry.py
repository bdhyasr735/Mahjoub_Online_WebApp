MODULE_NAME = "إدارة الموردين"
MODULE_ICON = "bi-people-fill" 

LINKS = {
    "قائمة الشركاء": "suppliers_bp.list_suppliers",
    "تعميد شريك جديد": "admin_suppliers_add_bp.add_supplier_or_staff"
}

def register_module(app):
    try:
        from .routes import suppliers_bp
        app.register_blueprint(suppliers_bp, url_prefix='/admin/suppliers')
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول الموردين: {e}")
