# 📂 apps/admin_suppliers_add/registry.py
from .routes import admin_suppliers_add_bp

def register_module(app):
    # تسجيل الموديول بالمسار المحدث
    app.register_blueprint(admin_suppliers_add_bp, url_prefix='/admin/suppliers')
    print("✅ [Registry]: تم تسجيل موديول 'admin_suppliers_add' بنجاح.")
