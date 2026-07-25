# coding: utf-8
# 📂 apps/suppliers_product/registry.py

"""
تسجيل تطبيق إدارة منتجات المورد في المنصة
"""

MODULE_NAME = "إدارة المنتجات"
MODULE_ICON = "fas fa-box"
SHOW_IN_SUPPLIER = True

# ✅ مفتاح الـ endpoint الصحيح بناءً على الـ routes
LINKS = {
    'suppliers_product_bp.products': '📦 قائمة المنتجات'
}


def register_module(app):
    """تسجيل تطبيق منتجات المورد في التطبيق الرئيسي"""
    try:
        from apps.suppliers_product.routes import (
            suppliers_product_bp,
            add_product_bp,
            edit_product_bp
        )
        
        # 1. تسجيل Blueprint عرض المنتجات
        if 'suppliers_product_bp' not in app.blueprints:
            app.register_blueprint(suppliers_product_bp, url_prefix='/supplier')
            print("✅ [Registry]: تم تسجيل 'suppliers_product_bp' بنجاح.")

        # 2. تسجيل Blueprint إضافة المنتجات
        if 'add_product_bp' not in app.blueprints:
            app.register_blueprint(add_product_bp, url_prefix='/supplier')
            print("✅ [Registry]: تم تسجيل 'add_product_bp' بنجاح.")

        # 3. تسجيل Blueprint تعديل المنتجات
        if 'edit_product_bp' not in app.blueprints:
            app.register_blueprint(edit_product_bp, url_prefix='/supplier')
            print("✅ [Registry]: تم تسجيل 'edit_product_bp' بنجاح.")
            
    except ImportError as e:
        print(f"❌ [Registry]: خطأ في استيراد مسارات suppliers_product: {e}")
    except Exception as e:
        print(f"❌ [Registry]: خطأ في تسجيل suppliers_product: {e}")
    
    return app
