# coding: utf-8
# 📂 apps/suppliers_product/registry.py

"""
تسجيل تطبيق إدارة منتجات المورد في المنصة
"""

MODULE_NAME = "إدارة المنتجات"
MODULE_ICON = "fas fa-box"
SHOW_IN_SUPPLIER = True

# ✅ مفتاح الـ endpoint أولاً، ثم النص الظاهري ثانياً (مطابق للمحفظة)
LINKS = {
    'supplier_product_bp.list_products': '📦 قائمة المنتجات'
}


def register_module(app):
    """تسجيل تطبيق منتجات المورد في التطبيق الرئيسي"""
    try:
        from apps.suppliers_product.routes import supplier_product_bp
        
        if 'supplier_product_bp' not in app.blueprints:
            app.register_blueprint(supplier_product_bp, url_prefix='/supplier')
            print("✅ [Registry]: تم تسجيل 'supplier_product_bp' بنجاح.")
        else:
            print("ℹ️ [Registry]: 'supplier_product_bp' مسجل مسبقاً.")
            
    except ImportError as e:
        print(f"❌ [Registry]: خطأ في استيراد suppliers_product: {e}")
    except Exception as e:
        print(f"❌ [Registry]: خطأ في تسجيل suppliers_product: {e}")
    
    return app
