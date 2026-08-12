# coding: utf-8
# 📂 apps/supplier_wallet/registry.py

import logging
from flask import url_for, session

# استيراد الـ Blueprint من routes وتصديره بالاسم المتوقع لدى Registry Loader
from apps.supplier_wallet.routes import wallet_bp as supplier_wallet_bp

logger = logging.getLogger(__name__)

MODULE_NAME = "محفظة المورد"
MODULE_ICON = "fa-wallet"
SHOW_IN_SUPPLIER = True

LINKS = {
    "supplier_wallet.wallet": "💳 كشف الحساب",
    "supplier_wallet.withdrawal_request": "💸 طلب سحب"
}

def register_module(app):
    try:
        if 'supplier_wallet' not in app.blueprints:
            app.register_blueprint(supplier_wallet_bp, url_prefix='/supplier/wallet')
            print("✅ [Registry Wallet]: تم تسجيل موديول محفظة الموردين بنجاح.")
        else:
            print("ℹ️ [Registry Wallet]: موديول المحفظة مسجل مسبقاً.")

        @app.context_processor
        def inject_supplier_wallet_meta():
            return dict(
                SUPPLIER_WALLET_THEME_COLOR='#4A154B',
                DEFAULT_PER_PAGE=10
            )

    except Exception as e:
        print(f"❌ [Registry Wallet]: خطأ أثناء تسجيل supplier_wallet: {e}")
    return app

def get_module_stats():
    try:
        supplier_id = session.get('user_id') or session.get('supplier_id')
        
        return {
            'total_balance': '48,500.00',
            'available_balance': '35,200.00',
            'pending_balance': '8,300.00',
            'has_wallet': True
        }
    except Exception as e:
        print(f"❌ [Registry Wallet Stats Error]: {e}")
        return {'total_balance': '0.00', 'available_balance': '0.00', 'pending_balance': '0.00', 'has_wallet': False}

def get_module_link():
    try:
        return url_for('supplier_wallet.wallet')
    except Exception as e:
        print(f"❌ [Registry Wallet Link Error]: {e}")
        return '/supplier/wallet'

def get_dashboard_card():
    stats = get_module_stats()
    return {
        'title': MODULE_NAME,
        'icon': MODULE_ICON,
        'link': get_module_link(),
        'stats': stats,
        'color': 'purple',
        'badge': stats.get('available_balance', '0'),
        'subtitle': f"المتاح: {stats.get('available_balance', '0')} ر.ي"
    }

__all__ = [
    'supplier_wallet_bp',
    'MODULE_NAME', 
    'MODULE_ICON', 
    'SHOW_IN_SUPPLIER', 
    'LINKS', 
    'register_module', 
    'get_module_stats', 
    'get_module_link', 
    'get_dashboard_card'
]
