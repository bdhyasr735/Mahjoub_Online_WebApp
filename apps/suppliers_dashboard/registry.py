# -*- coding: utf-8 -*-

# إعدادات الموديول للوحة تحكم الموردين
MODULE_NAME = "لوحة التحكم"
MODULE_ICON = "fa-tachometer-alt"
SHOW_IN_SUPPLIER = True

# الروابط التي ستظهر في القائمة الجانبية للمورد
NAV_ITEMS = [
    {
        "endpoint": "suppliers_dashboard.supplier_dashboard_index",
        "title": "الرئيسية",
        "icon": "fa-home"
    }
]

def register_module(app):
    """دالة تسجيل الموديول تلقائياً في التطبيق الرئيسي"""
    from apps.suppliers_dashboard import suppliers_dashboard_bp
    
    if 'suppliers_dashboard_core' not in app.blueprints:
        app.register_blueprint(suppliers_dashboard_bp)
    
    print("✅ [تسجيل موديول لوحة الموردين]: تم ربط مسارات وقوائم الموديول بنجاح.")
