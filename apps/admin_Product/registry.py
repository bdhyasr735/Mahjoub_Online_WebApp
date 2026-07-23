# coding: utf-8
# 📂 apps/admin_Product/registry.py

MODULE_NAME = "إدارة المنتجات"
MODULE_ICON = "fa-boxes"
SHOW_IN_SUPPLIER = False

# ✅ الروابط الأساسية
LINKS = {
    "admin_product_bp.manage_products": "📦 إدارة المنتجات",
    "admin_product_bp.add_product": "➕ إضافة منتج",
    "admin_product_bp.review_products": "📋 مراجعة المنتجات"  # ✅ أضف هذا
}


def register_module(app):
    try:
        # ✅ استيراد داخل الدالة يكسر دائرة الاستيراد
        from apps.admin_Product.routes import admin_product_bp
        
        # ✅ تسجيل Blueprint المنتجات
        if 'admin_product_bp' not in app.blueprints:
            app.register_blueprint(admin_product_bp, url_prefix='/admin')
            print("✅ [Registry]: تم تسجيل موديول إدارة المنتجات بنجاح.")
        else:
            print("ℹ️ [Registry]: admin_product_bp مسجل مسبقاً")
            
    except ImportError as e:
        print(f"❌ [Registry]: خطأ في استيراد admin_product: {e}")
    except Exception as e:
        print(f"❌ [Registry]: خطأ في تسجيل admin_product: {e}")
    
    return app
