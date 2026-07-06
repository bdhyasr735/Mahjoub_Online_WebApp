# coding: utf-8
# 📂 apps/suppliers_auth_portal/registry.py

from apps.suppliers_auth_portal.routes import suppliers_bp

def register_module(app):
    """
    تسجيل موديول بوابة الموردين (Auth Portal) في النظام
    """
    try:
        # نقوم بتسجيل الـ Blueprint مع url_prefix='/supplier'
        # هذا يعني أن صفحة الدخول ستكون متاحة على: /supplier/login
        app.register_blueprint(suppliers_bp, url_prefix='/supplier')
        
        print("✅ [Registry]: تم تسجيل موديول 'suppliers_auth_portal' بنجاح.")
        print("🔗 بوابة الدخول متاحة على المسار: /supplier/login")
        
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول 'suppliers_auth_portal': {e}")
