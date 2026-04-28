from flask import Blueprint

supplier_bp = Blueprint('supplier_panel', __name__, template_folder='templates')

from . import routes
