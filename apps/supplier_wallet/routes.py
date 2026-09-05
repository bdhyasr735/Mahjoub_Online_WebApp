# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/registry.py

from apps.supplier_wallet.routes import wallet_bp

MODULE_NAME = "الإدارة المالية"
ICON = "fas fa-wallet"
SHOW_IN_SUPPLIER = True

# تعريف الروابط التي تظهر في القائمة الجانبية للمورد
LINKS = {
    'supplier_wallet.wallet_dashboard': 'المحفظة والسحب',
    'supplier_wallet.transactions': 'حركة المحفظة',
    'supplier_wallet.withdraw': 'سحب الرصيد'
}

def register_module(app):
    """دالة تسجيل الموديول الديناميكي"""
    # تسجيل الـ Blueprint مع ربطه بالمتغيرات المطلوبة في النظام
    app.register_blueprint(wallet_bp)
    
    # دعم التوافقية مع الـ dynamic registration إذا كان يبحث عن الاسم القديم
    app.config.setdefault('supplier_wallet_bp', wallet_bp)
    
    print("✅ [الإدارة المالية]: تم تسجيل موديول المحفظة بنجاح.")
