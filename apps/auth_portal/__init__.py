from flask import Blueprint

auth_portal_bp = Blueprint('auth_portal', __name__, template_folder='templates')

from . import routes
