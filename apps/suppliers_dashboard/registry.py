# -*- coding: utf-8 -*-
# 📂 apps/suppliers_dashboard/registry.py

from apps.suppliers_dashboard.routes import suppliers_dashboard_bp

def register_suppliers_dashboard(app):
    """تسجيل وحدة لوحة تحكم الموردين (Suppliers Dashboard) في تطبيق الفلاسك الرئيسي."""
    app.register_blueprint(suppliers_dashboard_bp)
