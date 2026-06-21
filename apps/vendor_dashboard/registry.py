# 📂 apps/vendor_dashboard/registry.py

from apps.vendor_dashboard.routes import dashboard_bp

def register_app(app):
    """
    تسجيل لوحة تحكم الموردين ضمن المصنع الرئيسي.
    تم تعيين المسار الرئيسي للوحة على /supplier/dashboard
    """
    app.register_blueprint(dashboard_bp, url_prefix='/supplier')
