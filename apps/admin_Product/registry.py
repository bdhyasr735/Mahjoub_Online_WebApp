# coding: utf-8
# 📂 apps/admin_Product/registry.py

import apps.admin_Product.routes as product_routes
import apps.admin_Product.routes_edit as product_edit_routes
import apps.admin_Product.routes_add as product_add_routes

# ✅ استيراد review_bp
try:
    from apps.admin_Product.routes_review_products import review_bp
    REVIEW_EXISTS = True
except ImportError:
    REVIEW_EXISTS = False
    print("ℹ️ [Registry]: routes_review_products غير موجود")

MODULE_NAME = "إدارة المنتجات"
MODULE_ICON = "fa-boxes"
SHOW_IN_SUPPLIER = False

LINKS = {
    "admin_product_bp.manage_products": "📦 المنتجات",
    "admin_product_bp.add_product": "➕ إضافة منتج"
}

if REVIEW_EXISTS:
    LINKS["review_bp.review_products"] = "📋 مراجعة المنتجات"


def register_module(app):
    try:
        # ✅ تسجيل admin_product_bp
        if 'admin_product_bp' not in app.blueprints:
            app.register_blueprint(product_routes.admin_product_bp, url_prefix='/admin')
            print("✅ [Registry]: تم تسجيل 'admin_product_bp'")
        
        # ✅ تسجيل review_bp
        if REVIEW_EXISTS:
            if 'review_bp' not in app.blueprints:
                app.register_blueprint(review_bp, url_prefix='/admin')
                print("✅ [Registry]: تم تسجيل 'review_bp'")
                
    except Exception as e:
        print(f"❌ [Registry]: خطأ في التسجيل: {e}")
    
    return app
