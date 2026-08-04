# coding: utf-8
# 📂 apps/admin_orders/registry.py

# ❌ حذف السطر: from apps.admin_orders.routes import admin_orders_bp

MODULE_NAME = 'إدارة الطلبات'
MODULE_ICON = 'fas fa-boxes'
SHOW_IN_SUPPLIER = False

LINKS = {
    'admin_orders.list_admin_orders': 'عرض الطلبات',
}

def register_module(app):
    from apps.admin_orders.routes import admin_orders_bp  # ✅ الاستيراد هنا فقط
    app.register_blueprint(admin_orders_bp)
    print("✅ [Module]: تم تفعيل موديول إدارة الطلبات بنجاح.")
