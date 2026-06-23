# 📂 apps/suppliers_auth_portal/registry.py
from flask import redirect, url_for
from .routes import suppliers_bp

def register_app(app):
    # 1. تسجيل الـ Blueprint الخاص بالموردين
    app.register_blueprint(suppliers_bp, url_prefix='/suppliers')
    
    # 2. الجسر الذكي: تسجيل مسار وهمي يحاكي ما يبحث عنه المصنع
    # هذا يمنع خطأ BuildError ويقوم بتحويل أي نداء قديم إلى بوابة الموردين الجديدة
    app.add_url_rule(
        '/auth/login', 
        endpoint='auth_portal.login', 
        view_func=lambda: redirect(url_for('suppliers.login'))
    )
    
    print("✅ [System] تم تسجيل بوابة الموردين (Suppliers Portal) مع جسر توافق للمسارات القديمة")
