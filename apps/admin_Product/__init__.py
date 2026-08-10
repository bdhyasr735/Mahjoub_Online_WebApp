"""
admin_Product Blueprint Package
إدارة المنتجات والمتغيرات لمتجر محجوب أونلاين (www.mahjoub.online)
"""

from flask import Blueprint

admin_product_bp = Blueprint(
    'admin_Product',
    __name__,
    template_folder='templates',
    static_folder='static',
    url_prefix='/admin/products'
)

from . import routes
