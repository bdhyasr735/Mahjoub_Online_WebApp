# مثال: apps/admin_dashboard/__init__.py
from flask import Blueprint

# هذا الاسم 'admin_dashboard_bp' يجب أن يطابق ما استوردته في المصنع
admin_dashboard_bp = Blueprint('admin_dashboard_bp', __name__)

from . import routes
