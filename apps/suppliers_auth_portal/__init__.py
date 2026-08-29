# coding: utf-8
from flask import Blueprint

suppliers_auth_bp = Blueprint(
    'suppliers_auth_bp',
    __name__,
    url_prefix='/suppliers',
    template_folder='templates',
    static_folder='static'
)

# استيراد المسارات لتسجيلها تحت الكائن
from . import routes
