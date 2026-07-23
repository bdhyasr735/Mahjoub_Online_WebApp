# coding: utf-8
# 📂 apps/admin_Product/registry.py

import apps.admin_Product.routes as product_routes

MODULE_NAME = "إدارة المنتجات"
MODULE_ICON = "fa-boxes"
SHOW_IN_SUPPLIER = False

# ✅ الروابط الأساسية فقط
LINKS = {
    "admin_product_bp.manage_products": "📦 إدارة المنتجات",
    "admin_product_bp.add_product": "➕ إضافة منتج"
}


def register_module(app):
    try:
        if 'admin_product_bp' not in app.blueprints:
            app.register_blueprint(product_routes.admin_product_bp, url_prefix='/admin')
            print("✅ [Registry]: تم تسجيل 'admin_product_bp'")
        else:
            print("ℹ️ [Registry]: 'admin_product_bp' مسجل مسبقاً")
            
    except Exception as e:
        print(f"❌ [Registry]: خطأ في تسجيل admin_product: {e}")
    
    return app
