# coding: utf-8
# 📂 apps/suppliers_auth_portal/registry.py

from .routes import suppliers_bp

def register_module(app):
    """
    تسجيل موديول بوابة الموردين والمسوقين مع دعم النظام الديناميكي.
    """
    try:
        app.register_blueprint(suppliers_bp, url_prefix='/suppliers')
        
        # التأكد من وجود القاموس العام للموديولات
        if not hasattr(app, 'registered_modules'):
            app.registered_modules = {}
            
        # إضافة الموديول للرجستري (بدون إظهاره في الـ sidebar لأنه موديول auth)
        app.registered_modules['suppliers_auth_portal'] = MODULE_INFO
        
        print("✅ [Registry]: تم تسجيل موديول 'suppliers_auth_portal' بنجاح.")
    except Exception as e:
        print(f"🚨 [Registry Error]: {e}")

MODULE_INFO = {
    "display_name": "بوابة الموردين",
    "icon": "fas fa-lock",
    "show_in_supplier": False, # لا يظهر في الـ Sidebar الخاص بالمورد داخل اللوحة
    "show_in_admin": False,
    "links": {
        "تسجيل الدخول": "suppliers_auth.login" # تأكد من اسم الـ endpoint في routes
    }
}
