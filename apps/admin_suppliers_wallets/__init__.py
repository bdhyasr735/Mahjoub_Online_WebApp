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

    # استيراد المتحكمات لضمان ربط وتسجيل جميع المسارات والـ Endpoints بنجاح
    from apps.admin_suppliers_wallets.routes import suppliers_wallets_controller
    from apps.admin_suppliers_wallets.routes import withdraw_requests_controller

    return bp
