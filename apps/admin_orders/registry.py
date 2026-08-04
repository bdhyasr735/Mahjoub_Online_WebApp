# قديم (احذفه)
from apps.admin_orders import admin_orders_bp

# جديد (استبدله بهذا)
from flask import Blueprint  # أضف Blueprint إلى استيراد flask

# ثم عرّف الـ Blueprint هنا:
admin_orders_bp = Blueprint('admin_orders_bp', __name__, url_prefix='/admin/orders')
