# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/registry.py

from apps.supplier_wallet.routes import wallet_bp

# 🔗 تصدير اسم الـ Blueprint المطلوب لنظام التسجيل الديناميكي
supplier_wallet_bp = wallet_bp

MODULE_NAME = "الإدارة المالية"
ICON = "fas fa-wallet"
SHOW_IN_SUPPLIER = True

# تعريف الروابط لتظهر العنصرين المطلوبين فقط في القائمة الجانبية
LINKS = {
    'supplier_wallet.transactions': 'حركة المحفظة',
    'supplier_wallet.withdraw': 'سحب الرصيد'
}

def init_app(app):
    """دالة تسجيل الموديول في تطبيق Flask الرئيسي"""
    if 'supplier_wallet' not in app.blueprints and wallet_bp.name not in app.blueprints:
        app.register_blueprint(wallet_bp)
        print("✅ [الإدارة المالية]: تم تسجيل موديول المحفظة بنجاح.")

def register_module(app):
    """دالة تسجيل الموديول الديناميكي"""
    init_app(app)
