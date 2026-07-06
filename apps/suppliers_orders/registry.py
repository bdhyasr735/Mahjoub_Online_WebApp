# 📂 apps/suppliers_orders/registry.py

from apps.suppliers_orders.routes import suppliers_orders_bp

def register_module(app):
    # التسجيل مع url_prefix فريد لضمان عدم التعارض
    app.register_blueprint(suppliers_orders_bp, url_prefix='/suppliers/orders')
