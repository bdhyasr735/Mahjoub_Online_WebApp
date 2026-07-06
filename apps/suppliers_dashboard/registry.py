# 📂 apps/suppliers_dashboard/registry.py

from apps.suppliers_dashboard.routes import dashboard_bp

def register_module(app):
    try:
        app.register_blueprint(dashboard_bp, url_prefix='/suppliers')
        
        # إضافة الموديول إلى القائمة العامة (تأكد أن app.config يحتوي على registered_modules)
        if not hasattr(app, 'registered_modules'):
            app.registered_modules = {}
            
        app.registered_modules['suppliers_dashboard'] = MODULE_INFO
        
        print("✅ [Registry]: تم تسجيل وحدة 'suppliers_dashboard' بنجاح.")
    except Exception as e:
        print(f"🚨 [Registry Error]: فشل تسجيل وحدة لوحة تحكم المورد: {e}")

# تعريف بيانات الموديول ليتم عرضها في القائمة الجانبية ديناميكياً
MODULE_INFO = {
    "display_name": "لوحة المورد",
    "icon": "fas fa-th-large",
    "show_in_supplier": True, # ستظهر هذه الوحدة في القائمة الجانبية للمورد
    "links": {
        "الرئيسية": "suppliers_dashboard.dashboard"
    }
}

MODULE_CONFIG = {
    "module_name": "suppliers_dashboard",
    "version": "1.0.0",
    "status": "active",
    "base_url": "/suppliers"
}
