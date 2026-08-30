# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/__init__.py

from flask import Blueprint

# ✅ إنشاء البلوبرنت
bp = Blueprint(
    'suppliers_auth_portal',
    __name__,
    template_folder='templates/suppliers_auth_portal',
    url_prefix='/suppliers'
)

# ✅ استيراد مباشر من auth_routes
from .auth_routes import bp as auth_bp

# ✅ تسجيل البلوبرنت الفرعي
bp.register_blueprint(auth_bp)
