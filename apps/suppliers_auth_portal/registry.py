# coding: utf-8
# 📂 apps/suppliers_auth_portal/registry.py

from .routes import suppliers_bp

def register_module(app):
    """
    تسجيل موديول بوابة الموردين والمسوقين.
    يتم ربط الـ Blueprint بالمسار /suppliers ليتوافق مع رابط الـ fetch في login.html
    """
    app.register_blueprint(suppliers_bp, url_prefix='/suppliers')
    print("✅ [Registry] تم تسجيل موديول بوابة الموردين (suppliers_auth_portal) بنجاح.")
