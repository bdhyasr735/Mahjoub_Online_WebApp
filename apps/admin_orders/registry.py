# coding: utf-8
# 📂 apps/admin_orders/registry.py

MODULE_NAME = 'إدارة الطلبات'
MODULE_ICON = 'fas fa-boxes'
SHOW_IN_SUPPLIER = False

LINKS = {
    'admin_orders_bp.list_admin_orders': 'عرض الطلبات',
}

def register_module(app):
    from apps.admin_orders import admin_orders_bp
    app.register_blueprint(admin_orders_bp)
    
    # ✅ تسجيل مسارات وعناصر التحكم الخاصة بالمنتجات والموردين (items_bp)
    try:
        from apps.admin_orders.routes.items_controller import items_bp
        app.register_blueprint(items_bp)
        print("✅ [Module]: تم تسجيل items_bp بنجاح.")
    except Exception as e:
        print(f"⚠️ [Module]: لم يتم تسجيل items_bp: {e}")

    print("✅ [Module]: تم تفعيل موديول إدارة الطلبات بنجاح.")
    
    # 🔍 التحقق من تسجيل الـ endpoints
    print("🧾 [DEBUG] Admin Orders Endpoints:")
    for rule in app.url_map.iter_rules():
        if 'admin_orders' in rule.endpoint or 'items_bp' in rule.endpoint:
            print(f"   - {rule.endpoint} -> {rule.rule}")
