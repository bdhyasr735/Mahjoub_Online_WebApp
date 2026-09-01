# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/registry.py

import re
from flask import url_for
from flask_login import current_user
from apps.models.wallet_db import SupplierWallet
from apps.supplier_wallet.utils import get_current_supplier_id

MODULE_NAME = "الإدارة المالية"
MODULE_ICON = "fas fa-wallet"
SHOW_IN_SUPPLIER = True

# تعريف المتغيرات الثابتة كمرجع احتياطي (Fallback) لمنع حدوث خطأ Import Error
LINKS = {
    'supplier_wallet.transactions': 'حركة المحفظة',
    'supplier_wallet.withdraw': 'سحب الرصيد'
}

MENU_ITEMS = [
    {
        'endpoint': 'supplier_wallet.transactions',
        'title': 'حركة المحفظة',
        'icon': 'fas fa-exchange-alt'
    },
    {
        'endpoint': 'supplier_wallet.withdraw',
        'title': 'سحب الرصيد',
        'icon': 'fas fa-money-bill-wave'
    }
]

def get_dynamic_wallet_id():
    """استخراج معرّف المحفظة بالطريقة الآمنة للروابط"""
    try:
        supplier_id = get_current_supplier_id()
        w_id = 'general'
        if supplier_id:
            wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
            if wallet:
                w_id = str(getattr(wallet, 'wallet_code', None) or wallet.id)
            else:
                trade_name = getattr(current_user, 'trade_name', None)
                if trade_name:
                    slug = re.sub(r'[^\w\s-]', '', trade_name).strip().lower()
                    slug = re.sub(r'[-\s]+', '-', slug)
                    if slug:
                        w_id = slug
        return w_id
    except Exception:
        return 'general'

def get_links():
    w_id = get_dynamic_wallet_id()
    return {
        url_for('supplier_wallet.transactions', wallet_id=w_id): 'حركة المحفظة',
        url_for('supplier_wallet.withdraw', wallet_id=w_id): 'سحب الرصيد'
    }

def get_menu_items():
    w_id = get_dynamic_wallet_id()
    return [
        {
            'endpoint': 'supplier_wallet.transactions',
            'kwargs': {'wallet_id': w_id},
            'title': 'حركة المحفظة',
            'icon': 'fas fa-exchange-alt'
        },
        {
            'endpoint': 'supplier_wallet.withdraw',
            'kwargs': {'wallet_id': w_id},
            'title': 'سحب الرصيد',
            'icon': 'fas fa-money-bill-wave'
        }
    ]

def register_module(app):
    """
    تسجيل موديول المحفظة في التطبيق الرئيسي مع توفير القوائم الديناميكية للقالب الجانبي
    """
    from apps.supplier_wallet.routes import wallet_bp
    
    if 'supplier_wallet' not in app.blueprints:
        app.register_blueprint(wallet_bp, url_prefix='/supplier/wallet')
        print("✅ [Registry]: تم تسجيل بلوبرنت 'supplier_wallet' بنجاح.")

    if not hasattr(app, 'supplier_modules'):
        app.supplier_modules = {}
        
    module_payload = {
        'name': MODULE_NAME,
        'title': MODULE_NAME,
        'icon': MODULE_ICON,
        'url': url_for('supplier_wallet.wallet_dashboard', wallet_id=get_dynamic_wallet_id()),
        'links': get_links(),
        'menu_items': get_menu_items(),
        'show_in_supplier': SHOW_IN_SUPPLIER
    }

    # تسجيل الموديول تحت كلا المفتاحين لضمان التطابق التام
    app.supplier_modules['supplier_wallet'] = module_payload
    app.supplier_modules['suppliers_product'] = module_payload
    print("🟢 [التسجيل الديناميكي]: ✅ تم تحميل وتسجيل الموديول 'supplier_wallet' بنجاح.")
