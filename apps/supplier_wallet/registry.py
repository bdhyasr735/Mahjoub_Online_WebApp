# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/registry.py

from apps.supplier_wallet.routes import wallet_bp
from flask import url_for

# ============================================
# معلومات الموديول للتسجيل الديناميكي
# ============================================
MODULE_NAME = "supplier_wallet"
DISPLAY_NAME = "الإدارة المالية"
MODULE_ICON = "fa-coins"
SHOW_IN_SUPPLIER = True

def get_menu_items():
    """دالة ديناميكية لإنشاء الروابط مع wallet_id الفعلي"""
    from apps.supplier_wallet.utils import get_current_supplier_id
    from apps.models.wallet_db import SupplierWallet
    
    supplier_id = get_current_supplier_id()
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
    wallet_id = wallet.wallet_code if wallet else 'general'
    
    return {
        'supplier_wallet.transactions': ('حركة المحفظة', {'wallet_id': wallet_id}),
        'supplier_wallet.withdraw': ('سحب الرصيد', {'wallet_id': wallet_id})
    }

LINKS = {
    'supplier_wallet.transactions': 'حركة المحفظة',
    'supplier_wallet.withdraw': 'سحب الرصيد'
}

# ============================================
# دالة تسجيل الموديول
# ============================================
def register_module(app):
    if wallet_bp.name not in app.blueprints:
        app.register_blueprint(wallet_bp)
        print(f"✅ [Registry]: تم تسجيل المحفظة المالية بنجاح.")

def init_app(app):
    pass
