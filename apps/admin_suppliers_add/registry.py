# 📂 apps/admin_suppliers_add/registry.py
def register_module(app):
    try:
        from .routes import admin_suppliers_add_bp
        app.register_blueprint(admin_suppliers_add_bp, url_prefix='/admin/suppliers_add')
        print("✅ [Registry]: تم تسجيل موديول 'admin_suppliers_add' بنجاح.")
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول التعميد: {e}")
