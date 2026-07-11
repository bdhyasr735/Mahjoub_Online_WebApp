# coding: utf-8
# 📂 apps/suppliers_dashboard/registry.py

# هذه البيانات ستسمح للنظام بمعرفة أيقونة واسم الموديول
MODULE_NAME = "لوحة التحكم"
MODULE_ICON = "fas fa-home"
SHOW_IN_SUPPLIER = True

# تم تعديل ترتيب الـ LINKS لتصبح المفاتيح هي الـ endpoints
# النظام يبحث عن الـ endpoint في url_map ليتأكد من وجوده قبل عرضه
LINKS = {
    'suppliers_dashboard.dashboard': 'لوحة التحكم',
    'suppliers_dashboard.withdraw': 'سحب الرصيد',
    'suppliers_dashboard.settings': 'إعدادات المتجر'
}

def register_module(app):
    """
    تسجيل موديول لوحة التحكم (Dashboard)
    """
    from apps.suppliers_dashboard.routes import suppliers_dashboard_bp
    
    # التحقق من عدم تسجيل البلوبرنت أكثر من مرة
    if 'suppliers_dashboard' not in app.blueprints:
        app.register_blueprint(suppliers_dashboard_bp, url_prefix='/supplier')
        print("✅ [Registry]: تم تسجيل 'suppliers_dashboard' بنجاح.")
