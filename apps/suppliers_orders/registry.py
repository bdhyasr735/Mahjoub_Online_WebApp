# coding: utf-8
# 📂 apps/suppliers_orders/registry.py

# البيانات المطلوبة لنظام التسجيل التلقائي في __init__.py
MODULE_NAME = "طلبات الزبائن"
MODULE_ICON = "fas fa-shopping-cart"
SHOW_IN_SUPPLIER = True  # ليظهر في قائمة المورد الجانبية
LINKS = {
    'إدارة الطلبات': 'suppliers_orders.index'
}

def register_module(app):
    """
    تسجيل موديول الطلبات مع استيراد محلي لتجنب أخطاء التعريف.
    """
    # استيراد محلي داخل الدالة يمنع خطأ "Name not defined"
    from apps.suppliers_orders.routes import suppliers_orders_bp
    
    # التأكد من عدم التسجيل المكرر (حماية إضافية)
    if 'suppliers_orders' not in app.blueprints:
        app.register_blueprint(suppliers_orders_bp, url_prefix='/supplier/orders')
        print("✅ [Registry]: تم تسجيل موديول 'suppliers_orders' بنجاح.")
