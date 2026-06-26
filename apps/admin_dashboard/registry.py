# coding: utf-8
from .routes import admin_dashboard_bp

def register_module(app):
    """
    تسجيل موديول لوحة تحكم المسؤول في التطبيق.
    """
    app.register_blueprint(admin_dashboard_bp, url_prefix='/admin')
