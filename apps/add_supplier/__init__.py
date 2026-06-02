# 📂 apps/add_supplier/__init__.py

from flask import Blueprint
from apps.add_supplier.routes import add_supplier as add_supplier_bp

# يمكنك تعريف دالة تسجيل إذا لم تكن موجودة في مكان آخر
def register_add_supplier(app):
    """تسجيل بلوبرينت الموردين بشكل آمن"""
    try:
        app.register_blueprint(add_supplier_bp, url_prefix='/suppliers')
        print("✅ تم تسجيل بلوبرينت الموردين بنجاح.")
    except Exception as e:
        print(f"❌ فشل تسجيل بلوبرينت الموردين: {e}")

# إذا كنت تستخدم نمط الـ safe_register المخصص لديك:
# safe_register(add_supplier_bp, url_prefix='/suppliers')
