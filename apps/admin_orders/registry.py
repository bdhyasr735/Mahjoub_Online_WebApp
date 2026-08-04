# coding: utf-8
MODULE_NAME = 'إدارة الطلبات'
MODULE_ICON = 'fas fa-boxes'
SHOW_IN_SUPPLIER = False

LINKS = {
    'admin_orders.list_admin_orders': 'عرض الطلبات',
}

def register_module(app):
    from apps.admin_orders import admin_orders_bp  # الآن هذا الاستيراد صحيح
    app.register_blueprint(admin_orders_bp)
    print("✅ [Module]: تم تفعيل موديول إدارة الطلبات بنجاح.")
