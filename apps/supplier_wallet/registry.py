# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/registry.py

import logging
from flask import url_for

logger = logging.getLogger(__name__)

MODULE_NAME = "المحفظة والمالية"
MODULE_ICON = "fas fa-wallet"
SHOW_IN_SUPPLIER = True

LINKS = {
    "supplier_wallet_bp.wallet_dashboard": "📊 حركة المحفظة",
    "supplier_wallet_bp.withdraw": "💸 سحب الرصيد"
}

def register_module(app):
    try:
        from apps.supplier_wallet.routes import supplier_wallet_bp
        if 'supplier_wallet_bp' not in app.blueprints:
            app.register_blueprint(supplier_wallet_bp)
            print("✅ [Registry Wallet]: تم تسجيل موديول محفظة الموردين بنجاح.")
        else:
            print("ℹ️ [Registry Wallet]: موديول محفظة الموردين مسجل مسبقاً.")
    except ImportError as e:
        print(f"❌ [Registry Wallet]: خطأ في استيراد routes: {e}")
    except Exception as e:
        print(f"❌ [Registry Wallet]: خطأ في تسجيل supplier_wallet: {e}")
    return app

def get_module_link():
    try:
        return url_for('supplier_wallet_bp.wallet_dashboard')
    except Exception as e:
        print(f"❌ [Registry Wallet Link Error]: {e}")
        return '/supplier/wallet'

def get_dashboard_card():
    return {
        'title': MODULE_NAME,
        'icon': MODULE_ICON,
        'link': get_module_link(),
        'color': 'purple',
        'subtitle': 'إدارة الأرصدة والعمليات المالية'
    }

__all__ = ['MODULE_NAME', 'MODULE_ICON', 'SHOW_IN_SUPPLIER', 'LINKS', 'register_module', 'get_module_link', 'get_dashboard_card']
