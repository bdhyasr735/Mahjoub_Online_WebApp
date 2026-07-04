# coding: utf-8
# 📂 apps/admin_suppliers_add/registry.py

def register_module(app):
    """
    تسجيل الـ Blueprint الخاص بموديول إضافة الموردين.
    ملاحظة: تم نقل الاستيراد إلى داخل الدالة (Lazy Import) 
    لكسر حلقة الاستيراد (Circular Import) وضمان عمل الموديول في الخلفية.
    """
    try:
        from .routes import admin_suppliers_add_bp
        
        app.register_blueprint(admin_suppliers_add_bp, url_prefix='/admin/suppliers_add')
        print("✅ [Registry]: تم تسجيل موديول 'admin_suppliers_add' بنجاح (خلفية).")
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول 'admin_suppliers_add': {e}")
