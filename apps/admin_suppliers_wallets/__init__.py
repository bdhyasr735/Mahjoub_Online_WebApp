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

    # ✅ تسجيل مسارات المحافظ وطلبات السحب لتعمل الروابط فوراً
    from apps.admin_suppliers_wallets.routes import suppliers_wallets_controller
    from apps.admin_suppliers_wallets.routes import withdraw_requests_controller

    # ✅ الخطوة المفقودة: تسجيل الـ Blueprints الفرعية
    bp.register_blueprint(suppliers_wallets_controller.bp)
    bp.register_blueprint(withdraw_requests_controller.bp)

    return bp
