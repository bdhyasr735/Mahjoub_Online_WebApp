# coding: utf-8
from apps.suppliers_orders.routes import suppliers_orders_bp

def register_module(app):
    # تسجيل الـ Blueprint الخاص بالمورد فقط
    app.register_blueprint(suppliers_orders_bp, url_prefix='/suppliers_orders')
