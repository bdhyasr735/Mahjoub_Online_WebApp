# coding: utf-8
# apps/suppliers_auth_portal/__init__.py

from flask import Blueprint

suppliers_auth_bp = Blueprint(
    'suppliers_auth_bp',
    __name__,
    url_prefix='',
    template_folder='templates',
    static_folder='static'
)

# استيراد المسارات لتسجيلها تحت الكائن
from . import routes
