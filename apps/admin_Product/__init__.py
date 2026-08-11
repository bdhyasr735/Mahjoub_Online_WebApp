"""
متجر محجوب أونلاين (www.mahjoub.online) - Qumra Cloud Sandbox
Blueprint definition for admin_Product module.
"""
from flask import Blueprint

# تعريف الـ Blueprint لموديول إدارة المنتجات والمتغيرات
admin_product_bp = Blueprint(
    'admin_product',
    __name__,
    template_folder='templates',
    static_folder='static',
    url_prefix='/admin/products'
)

# استيراد المسارات لربط الدعم البرمجي
from . import routes