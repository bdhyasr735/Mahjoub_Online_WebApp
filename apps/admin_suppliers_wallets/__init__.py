# coding: utf-8
from flask import Blueprint

def create_admin_suppliers_wallets_blueprint():
    bp = Blueprint(
        'admin_suppliers_wallets',
        __name__,
        template_folder='templates',
        static_folder='static',
        url_prefix='/admin/suppliers-wallets'
    )

    # 🛠 الحل: استيراد وتسجيل المسارات هنا لربطها بالـ Blueprint
    from .routes import suppliers_wallets_controller, withdraw_requests_controller
    
    # تأكد أن المتحكمات تحتوي على @bp.route(...) وليس @app.route(...)
    # إذا كانت المتحكمات تستخدم bp بالفعل، فالتسجيل سيتم تلقائياً بمجرد الاستيراد
    
    return bp
