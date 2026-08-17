# coding: utf-8
from flask import Blueprint

def create_admin_suppliers_wallets_blueprint():
    # ✅ الحل: قمنا بتغيير الاسم من 'admin_suppliers_wallets' إلى 'admin_suppliers_wallets_main'
    # لضمان عدم تكرار الاسم مع الملف الآخر.
    bp = Blueprint(
        'admin_suppliers_wallets_main',
        __name__,
        template_folder='templates',
        static_folder='static',
        url_prefix='/admin/suppliers-wallets'
    )
    
    from . import suppliers_wallets_controller, withdraw_requests_controller
    # هذا السطر سيقوم بتسجيل الـ bp من الملف الآخر (الذي اسمه admin_suppliers_wallets)
    # كـ Blueprint فرعي تحت الـ bp الرئيسي الجديد (admin_suppliers_wallets_main)
    bp.register_blueprint(suppliers_wallets_controller.bp)
    
    return bp
