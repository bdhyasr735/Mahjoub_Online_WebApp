# -*- coding: utf-8 -*-
# 📂 apps/admin_Product/registry.py

MODULE_NAME = "إدارة المنتجات"
MODULE_ICON = "bi-box-seam"
SHOW_IN_ADMIN = True  # ضروري جداً ليظهر في سلايدر الإدارة

LINKS = {
    'admin_Product.list_products': 'عرض جميع المنتجات',
    'admin_Product.create_product': 'إضافة منتج جديد'
}

def register_module(app):
    try:
        from apps.admin_Product import admin_product_bp
        if 'admin_Product' not in app.blueprints:
            app.register_blueprint(admin_product_bp, url_prefix='/admin/products')
            print("✅ [Registry]: تم تسجيل admin_Product.")
    except Exception as e:
        print(f"❌ [Registry]: خطأ في تسجيل admin_Product: {e}")
