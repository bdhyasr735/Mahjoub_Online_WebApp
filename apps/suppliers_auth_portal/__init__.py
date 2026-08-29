from flask import Blueprint

suppliers_auth_bp = Blueprint(
    'suppliers_auth_bp',
    __name__,
    url_prefix='/suppliers',
    template_folder='templates',
    static_folder='static'
)

# استيراد المسارات من routes.py فقط
from . import routes
from . import registry_routes

__all__ = ['suppliers_auth_bp']
