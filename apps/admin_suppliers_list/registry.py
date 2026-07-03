# 📂 apps/admin_suppliers_list/registry.py

# استورد الاسم الصحيح المعرف في routes.py (وهو suppliers_bp)
from apps.admin_suppliers_list.routes import suppliers_bp

def register_module(app):
    """تسجيل موديول 'سجل الشركاء'."""
    
    # استخدم البلوبرنت المستورد للتو
    app.register_blueprint(suppliers_bp, url_prefix='/admin/suppliers')
    
    print("✅ [Registry]: تم تسجيل موديول 'admin_suppliers_list' بنجاح.")
