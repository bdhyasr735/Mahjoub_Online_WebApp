# apps/whatsapp_service/__init__.py
from flask import Blueprint

whatsapp_bp = Blueprint(
    'whatsapp_service',
    __name__,
    template_folder='templates',
    static_folder='static'
)

from . import routes
