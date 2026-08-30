# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/__init__.py

from flask import Blueprint

# ✅ تعديل مسار المجلد الأساسي للقوالب ليطابق بنية المشروع الصحيحة
bp = Blueprint(
    'suppliers_auth_portal',
    __name__,
    template_folder='templates',
    url_prefix='/suppliers'
)

# ✅ استيراد البلوبرنت الفرعي من auth_routes
from .auth_routes import bp as auth_bp

# ✅ تسجيل البلوبرنت الفرعي
bp.register_blueprint(auth_bp)

try:
    from . import seo_service
except ImportError:
    pass
