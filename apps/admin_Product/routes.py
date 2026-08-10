# coding: utf-8
# 📂 apps/admin_Product/registry.py

MODULE_NAME = 'إدارة المنتجات المتطورة'
MODULE_ICON = 'fas fa-box'
SHOW_IN_SUPPLIER = False

LINKS = {
    'admin_Product.list_products': 'جميع المنتجات',
    'admin_Product.create_product': 'إضافة منتج جديد',
}

def register_module(app):
    from apps.admin_Product import admin_product_bp
    app.register_blueprint(admin_product_bp)
    
    print("✅ [Module]: تم تفعيل موديول إدارة المنتجات المتطورة بنجاح.")
    
    # 🔍 التحقق من تسجيل الـ endpoints
    print("📦 [DEBUG] Admin Products Endpoints:")
    for rule in app.url_map.iter_rules():
        if 'admin_Product' in rule.endpoint:
            print(f"   - {rule.endpoint} -> {rule.rule}")
