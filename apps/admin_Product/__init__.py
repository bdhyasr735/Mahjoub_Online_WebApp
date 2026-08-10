from flask import Blueprint

admin_product_bp = Blueprint(
    'admin_Product',
    __name__,
    template_folder='templates',
    static_folder='static'
)

from . import routes
