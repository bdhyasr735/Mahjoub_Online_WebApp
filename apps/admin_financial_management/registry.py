# coding: utf-8
# 📂 apps/admin_financial_management/registry.py

from apps.admin_financial_management.routes import financial_mgmt_bp

def register_module(app):
    """
    تسجيل موديول الإدارة المالية للطلبات.
    """
    app.register_blueprint(financial_mgmt_bp, url_prefix='/admin/financial-management')
    print("✅ [Registry]: تم تسجيل موديول 'Admin Financial Management' بنجاح.")
