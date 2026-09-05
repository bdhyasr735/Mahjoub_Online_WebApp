# -*- coding: utf-8 -*-

MODULE_NAME = "الإدارة المالية"
ICON = "fa-wallet"
SHOW_IN_SUPPLIER = True  # أو False حسب رغبتك

# تعريف الروابط والقوائم الفرعية بشكل ديناميكي
NAV_ITEMS = [
    {
        "endpoint": "financial.wallet_movements",  # اسم الendpoint الخاص بحركة المحفظة لديك
        "title": "حركة المحفظة"
    },
    {
        "endpoint": "financial.withdraw_balance",   # اسم الendpoint الخاص بسحب الرصيد لديك
        "title": "سحب الرصيد"
    },
    {
        "endpoint": "financial.settlement_reports", # تقارير التسوية إن وجدت
        "title": "تقارير التسوية"
    }
]

def register_module(app):
    # تسجيل الـ Blueprint الخاص بالموديول هنا
    from apps.financial.routes import financial_bp
    app.register_blueprint(financial_bp, url_prefix='/financial')
    print("✅ [الإدارة المالية]: تم تسجيل الموديول بنجاح.")
