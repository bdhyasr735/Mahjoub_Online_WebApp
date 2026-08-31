# -*- coding: utf-8 -*-
# apps/auth_portal/__init__.py

"""
حزمة بوابة المصادقة السيادية الإدارية (Auth Portal Package)
لمنصة محجوب أونلاين
"""

from apps.auth_portal.routes import auth_portal_bp
from apps.auth_portal.registry import auth_registry, AuthPortalRegistry

__all__ = ['auth_portal_bp', 'auth_registry', 'AuthPortalRegistry']
