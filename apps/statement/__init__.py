from flask import Blueprint
statement_blueprint = Blueprint('statement_blueprint', __name__, template_folder='templates')
from . import routes
