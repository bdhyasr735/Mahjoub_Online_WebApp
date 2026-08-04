# coding: utf-8
# 📂 apps/admin_orders/registry.py

MODULE_NAME = "إدارة الطلبات"
MODULE_ICON = "fas fa-shopping-cart"
SHOW_IN_SUPPLIER = False  # هذه الوحدة للأدمن فقط

LINKS = {
    'admin_orders_bp.list_admin_orders': '📋 قائمة الطلبات'
}

def register_module(app):
    from apps.admin_orders import admin_orders_bp
    if 'admin_orders_bp' not in app.blueprints:
        app.register_blueprint(admin_orders_bp, url_prefix='/admin/orders')
        print("✅ [Registry]: تم تسجيل موديول 'admin_orders' بنجاح.")
    else:
        print("ℹ️ [Registry]: موديول 'admin_orders' مسجل مسبقاً.")
