# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/__init__.py

from flask import Blueprint

suppliers_bp = Blueprint(
    'suppliers_bp',
    __name__,
    template_folder='templates',
    static_folder='static'
)

def init_app(app):
    """تهيئة موديول بوابة الموردين."""
    pass
