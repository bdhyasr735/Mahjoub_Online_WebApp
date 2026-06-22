# 📂 apps/vendors/registry.py
from apps.vendors.routes import vendors_bp

def register_app(app):
    app.register_blueprint(vendors_bp, url_prefix='/vendors')
    print("✅ [Registry] تم تسجيل وحدة بوابات الدخول بنجاح على المسار /vendors")
