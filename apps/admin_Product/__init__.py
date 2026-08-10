# apps/admin_Product/__init__.py
from flask import Blueprint

admin_product_bp = Blueprint(
    'admin_Product',
    __name__,
    template_folder='templates',
    static_folder='static'
    # أزلنا url_prefix من هنا
)

from . import routes
