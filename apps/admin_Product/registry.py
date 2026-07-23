# coding: utf-8
# 📂 apps/admin_Product/registry.py

import apps.admin_Product.routes as product_routes

# ✅ حاول استيراد review_routes (إذا كان الملف موجوداً)
try:
    import apps.admin_Product.routes_review_products as review_routes
    REVIEW_EXISTS = True
except ImportError:
    REVIEW_EXISTS = False
    print("ℹ️ [Registry]: routes_review_products غير موجود، سيتم تخطيه")

# بيانات الموديول
MODULE_NAME = "إدارة المنتجات"
MODULE_ICON = "fa-boxes"
SHOW_IN_SUPPLIER = False

# الروابط
LINKS = {
    "admin_product_bp.manage_products": "📦 المنتجات",
    "admin_product_bp.add_product": "➕ إضافة منتج"
}

# ✅ إضافة رابط المراجعة فقط إذا كان الملف موجوداً
if REVIEW_EXISTS:
    LINKS["review_bp.review_products"] = "📋 مراجعة المنتجات"


def register_module(app):
    try:
        if 'admin_product_bp' not in app.blueprints:
            app.register_blueprint(product_routes.admin_product_bp, url_prefix='/admin')
            print("✅ [Registry]: تم تسجيل 'admin_product_bp'")
        
        # ✅ تسجيل review_bp فقط إذا كان الملف موجوداً
        if REVIEW_EXISTS:
            if 'review_bp' not in app.blueprints:
                app.register_blueprint(review_routes.review_bp, url_prefix='/admin')
                print("✅ [Registry]: تم تسجيل 'review_bp'")
                
    except Exception as e:
        print(f"❌ [Registry]: خطأ في التسجيل: {e}")
    
    return app
