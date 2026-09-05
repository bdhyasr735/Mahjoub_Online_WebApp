# apps/suppliers_dashboard/__init__.py
from flask import Blueprint

suppliers_dashboard_bp = Blueprint(
    'suppliers_dashboard',
    __name__,
    template_folder='templates',
    static_folder='static'
)

from apps.suppliers_dashboard import routes
