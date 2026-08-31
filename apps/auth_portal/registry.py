# -*- coding: utf-8 -*-
# apps/auth_portal/registry.py

"""
ملف التسجيل المركزي لبوابة المصادقة السيادية
"""

from .routes import init_app, auth_portal_bp

def register_auth_portal(app):
    """تسجيل وتهيئة مكونات بوابة المصادقة في التطبيق الرئيسي"""
    return init_app(app)
