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

# ✅ استيراد routes.py بعد إنشاء البلوبرنت
from . import auth_routes

# ✅ تسجيل البلوبرنت الفرعي
bp.register_blueprint(auth_routes.bp)
