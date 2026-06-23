# 📂 apps/suppliers_auth_portal/registry.py (النسخة الآمنة)
from flask import redirect, url_for

def register_app(app):
    try:
        # الاستيراد داخل الدالة (Lazy Import) يمنع انهيار النظام عند الإقلاع
        from .routes import suppliers_bp
        
        # 1. تسجيل الـ Blueprint الخاص بالموردين
        app.register_blueprint(suppliers_bp, url_prefix='/suppliers')
        
        # 2. الجسر الذكي
        app.add_url_rule(
            '/auth/login', 
            endpoint='auth_portal.login', 
            view_func=lambda: redirect(url_for('suppliers.login'))
        )
        
        print("✅ [System] تم تسجيل بوابة الموردين (Suppliers Portal) بنجاح.")
        
    except Exception as e:
        # في حال وجود خطأ في routes.py الخاص بالموردين، 
        # سنقوم بطباعة الخطأ فقط ولن ينهار النظام.
        print(f"⚠️ [Isolation] تعذر تسجيل بوابة الموردين بسبب خطأ في كود الموردين: {e}")
