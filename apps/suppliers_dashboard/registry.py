# coding: utf-8
from apps.suppliers_auth.routes import suppliers_auth_bp

def register_module(app):
    try:
        # تسجيل مسار الدخول والخروج
        app.register_blueprint(suppliers_auth_bp, url_prefix='/supplier')
        print("✅ [Registry]: تم تسجيل موديول 'suppliers_auth' بنجاح.")
    except Exception as e:
        print(f"❌ [Registry Error]: {e}")
