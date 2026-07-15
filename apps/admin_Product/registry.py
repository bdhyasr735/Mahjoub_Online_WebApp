# 📂 apps/admin_Product/registry.py

from .routes import admin_product_bp

MODULE_NAME = "إدارة المنتجات"
MODULE_ICON = "fas fa-box-open"
SHOW_IN_SUPPLIER = False 

# الترتيب الصحيح هو { "endpoint": "اسم الرابط" }
LINKS = {
    "admin_product.manage_products": "قائمة المنتجات",
    "admin_product.add_product": "إضافة منتج"
}

def register_module(app):
    """
    تسجيل موديول 'إدارة المنتجات' في النظام المركزي.
    """
    try:
        # تسجيل البلوبرينت تحت المسار الرئيسي /admin/products
        app.register_blueprint(admin_product_bp, url_prefix='/admin/products')
        
        print("✅ [Registry]: تم تسجيل موديول 'إدارة المنتجات' بنجاح.")
    
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول 'إدارة المنتجات': {e}")
