from flask import Blueprint

admin_treasury_bp = Blueprint(
    'admin_treasury',
    __name__,
    template_folder='../templates',
    url_prefix='/admin/treasury'
)

# استيراد المتحكم هنا ليتم تسجيل المسارات
from apps.admin_treasury.routes import treasury_controller
