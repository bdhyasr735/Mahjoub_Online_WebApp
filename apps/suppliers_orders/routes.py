# coding: utf-8
from apps.suppliers_orders.routes import suppliers_orders_bp

def register_module(app):
    # تسجيل الـ Blueprint بمسار منظم
    app.register_blueprint(suppliers_orders_bp, url_prefix='/suppliers/orders')
    
    if not hasattr(app, 'registered_modules'):
        app.registered_modules = {}
        
    # تسجيل الموديول في القاموس العام
    app.registered_modules['suppliers_orders_portal'] = {
        "display_name": "طلبات الزبائن",
        "icon": "fas fa-shopping-cart",
        "show_in_supplier": True,
        "links": {
            "قائمة الطلبات": "suppliers_orders_portal.dashboard"
        }
    }
