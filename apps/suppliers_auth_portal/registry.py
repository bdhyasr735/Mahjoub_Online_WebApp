# coding: utf-8
# 📂 apps/suppliers_dashboard/registry.py

from apps.suppliers_dashboard.routes import suppliers_dashboard_bp

# بيانات الموديول (تستخدم في الـ __init__.py للـ Auto-Discovery)
MODULE_NAME = "لوحة التحكم"
MODULE_ICON = "fas fa-tachometer-alt"
SHOW_IN_SUPPLIER = True
LINKS = {
    "الرئيسية": "suppliers_dashboard.dashboard"
}

def register_module(app):
    """
    تسجيل موديول لوحة تحكم الموردين
    """
    try:
        # ملاحظة: بما أن الـ Auth Portal يستخدم url_prefix='/supplier'
        # فإن تسجيل الـ Dashboard بنفس الـ prefix سيجعل المسارات تندمج بشكل سليم
        # بشرط أن تكون الراوتس في routes.py تبدأ بـ /dashboard وليس /supplier/dashboard
        app.register_blueprint(suppliers_dashboard_bp, url_prefix='/supplier')
        
        print("✅ [Registry]: تم تسجيل موديول 'suppliers_dashboard' بنجاح.")
        print("🔗 الداشبورد متاحة على المسار: /supplier/dashboard")
        
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول 'suppliers_dashboard': {e}")
