# 📂 apps/admin_platform_treasury/registry.py
from .routes import treasury_bp

def register_module(app):
    # تسجيل موديول الخزينة
    app.register_blueprint(treasury_bp, url_prefix='/admin/treasury')
    print("✅ [Registry]: تم تسجيل موديول 'treasury' بنجاح.")
