# coding: utf-8
# 📂 apps/suppliers_dashboard/registry.py

# هذه البيانات ستسمح للنظام بمعرفة أيقونة واسم الموديول
MODULE_NAME = "الرئيسية"
MODULE_ICON = "fas fa-home"
SHOW_IN_SUPPLIER = True

# تعريف الروابط التي سيستخدمها النظام
LINKS = {
    'لوحة التحكم': 'suppliers_dashboard.dashboard'
}

def register_module(app):
    """
    تسجيل موديول لوحة التحكم (Dashboard)
    """
    from apps.suppliers_dashboard.routes import suppliers_dashboard_bp
    
    if 'suppliers_dashboard' not in app.blueprints:
        app.register_blueprint(suppliers_dashboard_bp, url_prefix='/supplier')
        print("✅ [Registry]: تم تسجيل 'suppliers_dashboard' بنجاح.")
