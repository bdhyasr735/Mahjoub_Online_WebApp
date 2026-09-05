# apps/suppliers_dashboard/__init__.py
from flask import Blueprint

suppliers_dashboard_bp = Blueprint(
    'suppliers_dashboard',
    __name__,
    template_folder='templates',
    static_folder='static'
)

def register_module(app):
    """دالة التسجيل الديناميكي لتتوافق مع نظام المحمل العام في محجوب أونلاين"""
    app.register_blueprint(suppliers_dashboard_bp, url_prefix='/suppliers')
    # يمكنك تعديل الـ url_prefix حسب مسار التطبيق لديك

from apps.suppliers_dashboard import routes
