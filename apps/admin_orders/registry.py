# coding: utf-8
# 📂 apps/admin_orders/registry.py

MODULE_NAME = 'إدارة الطلبات'
MODULE_ICON = 'fas fa-boxes'
SHOW_IN_SUPPLIER = False

LINKS = {
    'admin_orders_bp.list_admin_orders': 'عرض الطلبات',   # ✅ تم التصحيح
}

def register_module(app):
    from apps.admin_orders import admin_orders_bp  # ✅ الاستيراد صحيح (لأن الـ __init__.py يُصدره)
    app.register_blueprint(admin_orders_bp)
    print("✅ [Module]: تم تفعيل موديول إدارة الطلبات بنجاح.")
