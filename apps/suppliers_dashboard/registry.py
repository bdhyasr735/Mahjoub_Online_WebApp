# coding: utf-8
# 📂 apps/suppliers_dashboard/registry.py

# تأكد أنك تستورد الاسم الجديد الذي عرفناه في routes.py
from apps.suppliers_dashboard.routes import suppliers_dashboard_bp 

MODULE_NAME = "لوحة التحكم"
MODULE_ICON = "fas fa-tachometer-alt"
SHOW_IN_SUPPLIER = True

LINKS = {
    "الرئيسية": "suppliers_dashboard.dashboard"
}

def register_module(app):
    try:
        # تأكد من استخدام المتغير الجديد
        app.register_blueprint(suppliers_dashboard_bp, url_prefix='/supplier')
        print("✅ [Registry]: تم تسجيل موديول 'suppliers_dashboard' بنجاح.")
    except Exception as e:
        print(f"❌ [Registry Error]: {e}")
