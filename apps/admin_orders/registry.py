# 📂 apps/admin_orders/registry.py

MODULE_NAME = 'إدارة الطلبات'
MODULE_ICON = 'fas fa-boxes'
SHOW_IN_SUPPLIER = False

LINKS = {
    'admin_orders_bp.list_admin_orders': 'عرض الطلبات',
}

def register_module(app):
    # 1. تسجيل موديول الطلبات الرئيسي أولاً
    from apps.admin_orders.routes.orders import admin_orders_bp
    app.register_blueprint(admin_orders_bp)
    print("✅ [Module]: تم تسجيل admin_orders_bp بنجاح.")

    # 2. محاولة تسجيل items_bp بشكل منفصل دون إيقاف الموديول
    try:
        from apps.admin_orders.routes.items_controller import items_bp
        app.register_blueprint(items_bp)
        print("✅ [Module]: تم تسجيل items_bp بنجاح.")
    except Exception as e:
        print(f"⚠️ [Module]: تعذر تسجيل items_bp: {e}")
