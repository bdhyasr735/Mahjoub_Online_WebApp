# 📂 apps/suppliers_add/registry.py
from apps.suppliers_add.routes import suppliers_add_bp

def register_module(app):
    """تسجيل بلوبرينت إضافة الموردين"""
    app.register_blueprint(suppliers_add_bp, url_prefix='/admin/suppliers')
    print("✅ [Registry]: تم تسجيل موديول 'suppliers_add' بنجاح.")
