# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/registry.py

from apps.supplier_wallet.routes import wallet_bp

MODULE_NAME = "الإدارة المالية"
ICON = "fas fa-wallet"
SHOW_IN_SUPPLIER = True

# تعريف الروابط لتظهر العنصرين المطلوبين فقط في القائمة الجانبية
LINKS = {
    'supplier_wallet.transactions': 'حركة المحفظة',
    'supplier_wallet.withdraw': 'سحب الرصيد'
}

def register_module(app):
    """دالة تسجيل الموديول الديناميكي"""
    app.register_blueprint(wallet_bp)
    
    # دعم التوافقية مع النظام الديناميكي
    app.config.setdefault('supplier_wallet_bp', wallet_bp)
    
    print("✅ [الإدارة المالية]: تم تسجيل موديول المحفظة بنجاح.")
