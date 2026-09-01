# 📂 مثال: apps/suppliers_wallet/registry.py

from apps.suppliers_wallet.routes import suppliers_wallet_bp

MODULE_NAME = "محفظة المورد"
DISPLAY_NAME = "المحفظة المالية"
MODULE_ICON = "fa-wallet"
IS_LAYOUT_CONTAINER = False # سيتم تضمينه في القائمة الجانبية

# الروابط التي ستظهر في القائمة الفرعية (الاسم البرمجي للمسار : العنوان المعروض)
LINKS = {
    'suppliers_wallet.index': 'رصيد المحفظة',
    'suppliers_wallet.transactions': 'سجل العمليات المالي',
    'suppliers_wallet.withdraw': 'طلب سحب الرصيد'
}

def register_module(app):
    if suppliers_wallet_bp.name not in app.blueprints:
        app.register_blueprint(suppliers_wallet_bp)
        print(f"✅ [Registry]: تم تسجيل {DISPLAY_NAME} بنجاح.")
