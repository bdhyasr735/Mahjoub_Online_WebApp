from flask import Blueprint

admin_bp = Blueprint(
    'admin_panel', 
    __name__, 
    template_folder='templates', # يشير إلى مجلد templates الداخلي
    static_folder='static'
)

from . import routes
