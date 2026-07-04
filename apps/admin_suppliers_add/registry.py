# 📂 apps/admin_suppliers_add/registry.py
# ملاحظة: لا نضع LINKS هنا إذا كنا لا نريد ظهور رابط إضافي في القائمة الجانبية، 
# أو يمكننا إضافته إذا أردنا.

def register_module(app):
    try:
        from .routes import admin_suppliers_add_bp
        app.register_blueprint(admin_suppliers_add_bp, url_prefix='/admin/suppliers_add')
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول التعميد: {e}")
