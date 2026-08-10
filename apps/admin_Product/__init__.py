"""
admin_Product Blueprint Package
إدارة المنتجات والمتغيرات لمتجر محجوب أونلاين (www.mahjoub.online)
"""

import os
from flask import Blueprint

template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

admin_product_bp = Blueprint(
    'admin_Product',
    __name__,
    template_folder=template_dir,
    static_folder='static',
    url_prefix='/admin/products'
)

from . import routes
