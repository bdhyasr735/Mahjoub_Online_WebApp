from flask import Blueprint

suppliers_dashboard_bp = Blueprint(
    'suppliers_dashboard_core',
    __name__,
    template_folder='templates',  # تأكد من تحديد مسار مجلد القوالب نسبياً لمكان الموديول
    url_prefix='/supplier'
)
