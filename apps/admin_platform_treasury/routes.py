# coding: utf-8
# 📂 apps/admin_platform_treasury/registry.py

# تأكد أنك تستورد 'treasury_bp' وليس أي اسم آخر
from apps.admin_platform_treasury.routes import treasury_bp

# إخفاء الموديول من القائمة الرئيسية لمنع التكرار (بما أننا وضعنا الرابط في الرقابة المالية)
LINKS = {} 

def register_module(app):
    try:
        # تسجيل الـ Blueprint باستخدام الاسم الصحيح 'treasury_bp'
        app.register_blueprint(treasury_bp, url_prefix='/admin/treasury')
        print("✅ [Registry]: تم تسجيل موديول 'Admin Platform Treasury' بنجاح.")
    except Exception as e:
        print(f"❌ [Registry Error]: {e}")
