# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/__init__.py

from flask import Blueprint

bp = Blueprint(
    'suppliers_auth_portal',
    __name__,
    template_folder='templates/suppliers_auth_portal',
    url_prefix='/suppliers'
)

from . import auth_routes, seo_service

bp.register_blueprint(auth_routes.bp)
