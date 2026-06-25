# coding: utf-8
# 📂 apps/suppliers_dashboard/registry.py

from apps.suppliers_dashboard.routes import dashboard_bp

def register_module(app):
    """
    تسجيل لوحة تحكم المورد (Supplier Dashboard)
    تم ضبط الـ url_prefix ليكون '/suppliers' ليتطابق مع طلبات المتصفح.
    """
    try:
        # تسجيل الـ Blueprint بمسار '/suppliers' 
        # المسار الكامل سيصبح: /suppliers/dashboard
        app.register_blueprint(dashboard_bp, url_prefix='/suppliers')
        
        print("✅ [Registry]: تم تسجيل وحدة 'suppliers_dashboard' بنجاح على المسار (/suppliers).")
        
    except Exception as e:
        print(f"🚨 [Registry Error]: فشل تسجيل وحدة لوحة تحكم المورد: {e}")

# إعدادات الموديول الفنية
MODULE_CONFIG = {
    "module_name": "suppliers_dashboard",
    "version": "1.0.0",
    "status": "active"
}
