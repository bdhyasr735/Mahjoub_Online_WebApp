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
    print("✅ [Module]: تم تفعيل موديول إدارة الطلبات بنجاح.")
    
    # 🔍 التحقق من تسجيل الـ endpoints
    print("🧾 [DEBUG] Admin Orders Endpoints:")
    for rule in app.url_map.iter_rules():
        if 'admin_orders' in rule.endpoint:
            print(f"   - {rule.endpoint} -> {rule.rule}")
