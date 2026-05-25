from flask import Blueprint

statement_blueprint = Blueprint(
    'statement_blueprint',  # تأكد أن هذا الاسم هو 'statement_blueprint'
    __name__, 
    template_folder='templates'
)

from apps.statement import routes
