# -*- coding: utf-8 -*-
# 📂 apps/auth_portal/registry.py

from apps.auth_portal.routes import auth_portal_bp

def register_auth_portal(app):
    """
    دالة تسجيل البوابة السيادية الإدارية في التطبيق الرئيسي لـ Flask
    """
    app.register_blueprint(auth_portal_bp)
