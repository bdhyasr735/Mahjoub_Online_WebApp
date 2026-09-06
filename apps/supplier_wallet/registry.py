# -*- coding: utf-8 -*-
from flask import Blueprint

# تعريف الـ Blueprint الخاص بالمحفظة مع تحديد المسار والقوالب
supplier_wallet_bp = Blueprint(
    'supplier_wallet',
    __name__,
    template_folder='templates/supplier_wallet',
    url_prefix='/supplier/wallet'
)

# بيانات العرض في القائمة الجانبية للموردين
MODULE_NAME = "محفظة المورد"
MODULE_ICON = "fa-wallet"
SHOW_IN_SUPPLIER = True

NAV_ITEMS = [
    {
        'endpoint': 'supplier_wallet.wallet_dashboard',
        'title': 'لوحة المحفظة والعمليات'
    }
]

def register_module(app):
    """دالة التسجيل الديناميكي التي يستدعيها النظام الرئيسي"""
    from apps.supplier_wallet import routes  # استيراد المسارات لتفعيلها
    app.register_blueprint(supplier_wallet_bp)
    print("🟢 [موديول محفظة المورد]: تم تسجيل البلوبرنت بنجاح.")
