# coding: utf-8
# 📂 apps/suppliers_orders/registry.py

from apps.suppliers_orders.routes import suppliers_orders_bp

def register_module(app):
    """
    تسجيل موديول طلبات الزبائن وتزويد النظام بمعلومات العرض الديناميكي.
    """
    try:
        # تسجيل الـ Blueprint باسم فريد لتجنب التضارب
        app.register_blueprint(suppliers_orders_bp, url_prefix='/suppliers/orders')
        
        # التأكد من وجود القاموس العام للموديولات
        if not hasattr(app, 'registered_modules'):
            app.registered_modules = {}
            
        # استخدام اسم مفتاح فريد في القاموس
        app.registered_modules['suppliers_orders_portal'] = MODULE_INFO
        
        print("✅ [Registry]: تم تسجيل موديول 'suppliers_orders_portal' بنجاح.")
    except Exception as e:
        print(f"🚨 [Registry Error]: {e}")

# تعريف معلومات العرض
MODULE_INFO = {
    "display_name": "طلبات الزبائن",
    "icon": "fas fa-shopping-cart",
    "show_in_supplier": True, # سيظهر في القائمة الجانبية للمورد
    "show_in_admin": True,
    "links": {
        "إدارة الطلبات": "suppliers_orders_portal.dashboard" # تأكد أن هذا الـ endpoint مطابق لاسم الـ route في routes.py
    }
}
