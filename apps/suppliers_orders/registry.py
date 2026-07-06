# coding: utf-8
from apps.suppliers_orders.routes import suppliers_orders_bp

# البيانات المطلوبة لنظام التسجيل التلقائي
MODULE_NAME = "طلبات الزبائن"
MODULE_ICON = "fas fa-shopping-cart"
SHOW_IN_SUPPLIER = True  # ليظهر في لوحة المورد
LINKS = {
    'جميع الطلبات': 'suppliers_orders.list_orders',
    'طلبات معلقة': 'suppliers_orders.pending_orders'
}

def register_module(app):
    """
    تسجيل موديول طلبات الزبائن مع الحماية من التسجيل المتكرر.
    """
    if 'suppliers_orders' not in app.blueprints:
        app.register_blueprint(suppliers_orders_bp, url_prefix='/supplier/orders')
        print("✅ [Registry]: تم تسجيل موديول 'suppliers_orders' بنجاح.")
    else:
        print("⚠️ [Registry]: موديول 'suppliers_orders' مسجل مسبقاً، تم التخطي.")
