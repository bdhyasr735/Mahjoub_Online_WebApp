# apps/suppliers_auth_portal/__init__.py
from flask import Blueprint

suppliers_auth_bp = Blueprint(
    'suppliers_auth_bp',
    __name__,
    template_folder='templates',
    static_folder='static',
    url_prefix='/suppliers'
)

from apps.suppliers_auth_portal import routes
