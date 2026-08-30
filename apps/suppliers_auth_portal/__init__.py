# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/__init__.py

from flask import Blueprint

# ✅ إنشاء البلوبرنت الرئيسي
bp = Blueprint(
    'suppliers_auth_portal',
    __name__,
    template_folder='templates/suppliers_auth_portal',
    url_prefix='/suppliers'
)

# ✅ استيراد البلوبرنت الفرعي من auth_routes
from .auth_routes import bp as auth_bp

# ✅ تسجيل البلوبرنت الفرعي
bp.register_blueprint(auth_bp)

# ✅ ربط خدمات الـ SEO أو تفعيلها إن وجدت في seo_service
try:
    from . import seo_service
except ImportError:
    pass
