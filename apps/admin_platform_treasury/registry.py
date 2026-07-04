# coding: utf-8
# 📂 apps/admin_platform_treasury/registry.py

# نجعلها فارغة لأننا قمنا بتجميعها في موديول 'الرقابة المالية'
LINKS = {} 

def register_module(app):
    """
    تسجيل الموديول وتفعيله (يعمل في الخلفية، ولا يظهر في القائمة كعنصر مستقل).
    """
    try:
        from apps.admin_platform_treasury.routes import treasury_bp
        app.register_blueprint(treasury_bp, url_prefix='/admin/treasury')
        print("✅ [Registry]: تم تسجيل موديول 'Admin Platform Treasury' بنجاح (مدمج في الرقابة المالية).")
    except Exception as e:
        print(f"❌ [Registry Error]: {e}")
