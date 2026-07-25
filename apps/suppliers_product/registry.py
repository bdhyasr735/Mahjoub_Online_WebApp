# coding: utf-8
# 📂 apps/suppliers_product/registry.py

"""
تسجيل تطبيق منتجات المورد في المنصة
"""

MODULE_NAME = "إدارة المنتجات"
MODULE_ICON = "fas fa-box-open"
SHOW_IN_SUPPLIER = True

# ✅ الروابط التي تظهر في القائمة الجانبية للمورد (تم عكس المفتاح والقيمة لتتوافق مع نظام المنصة)
LINKS = {
    '📦 قائمة المنتجات': 'suppliers_product_bp.products',
    '➕ إضافة منتج جديد': 'add_product_bp.add_product_page'
}


class SupplierProductRegistry:
    """مسجل المكونات والإضافات لمنتجات الموردين"""
    
    def __init__(self):
        self._components = {}

    def register(self, name, component):
        """تسجيل مكون جديد"""
        self._components[name] = component

    def get(self, name):
        """جلب مكون مسجل"""
        return self._components.get(name)

    def list_components(self):
        """عرض جميع المكونات المسجلة"""
        return list(self._components.keys())


# ====== SINGLETON ======
supplier_product_registry = SupplierProductRegistry()


def register_module(app):
    """تسجيل تطبيق منتجات المورد في التطبيق الرئيسي"""
    try:
        from apps.suppliers_product.routes import (
            suppliers_product_bp, 
            add_product_bp, 
            edit_product_bp
        )
        
        # تسجيل الـ Blueprints إذا لم تكن مسجلة مسبقاً
        if 'suppliers_product_bp' not in app.blueprints:
            app.register_blueprint(suppliers_product_bp, url_prefix='/supplier')
        if 'add_product_bp' not in app.blueprints:
            app.register_blueprint(add_product_bp, url_prefix='/supplier')
        if 'edit_product_bp' not in app.blueprints:
            app.register_blueprint(edit_product_bp, url_prefix='/supplier')
            
        print("✅ [Registry]: تم تسجيل 'suppliers_product' بنجاح.")
        
    except ImportError as e:
        print(f"❌ [Registry]: خطأ في استيراد suppliers_product: {e}")
    except Exception as e:
        print(f"❌ [Registry]: خطأ في تسجيل suppliers_product: {e}")
    
    return app
