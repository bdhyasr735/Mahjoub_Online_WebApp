# 📂 apps/suppliers_auth_portal/registry.py
from .routes import suppliers_bp

def register_app(app):
    # تغيير الرابط من '/vendors' إلى '/suppliers'
    app.register_blueprint(suppliers_bp, url_prefix='/suppliers')
    print("✅ [Registry] تم تسجيل بوابة الموردين على المسار /suppliers")
