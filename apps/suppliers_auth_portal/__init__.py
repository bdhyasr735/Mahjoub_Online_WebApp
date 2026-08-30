# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/__init__.py

from flask import Blueprint  # ✅ تأكد من وجود هذا السطر

bp = Blueprint(
    'suppliers_auth_portal',
    __name__,
    template_folder='templates/suppliers_auth_portal',
    url_prefix='/supplier'
)

from . import auth_login, auth_register, auth_recovery, seo_service

bp.register_blueprint(auth_login.bp)
bp.register_blueprint(auth_register.bp)
bp.register_blueprint(auth_recovery.bp)
