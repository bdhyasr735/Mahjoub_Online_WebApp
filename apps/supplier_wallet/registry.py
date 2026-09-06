# coding: utf-8
# 📂 apps/supplier_wallet/registry.py

import logging
from flask import url_for, session

logger = logging.getLogger(__name__)

MODULE_NAME = "محفظة المورد"
MODULE_ICON = "fas fa-wallet"
SHOW_IN_SUPPLIER = True

LINKS = {
    "supplier_wallet_bp.supplier_wallet_view": "💰 إدارة المحفظة",
    "supplier_wallet_bp.wallet_transactions": "📊 سجل المعاملات"
}

def register_module(app):
    try:
        # ✅ التصحيح هنا: استخدام الاسم المفرد supplier_wallet بدلاً من suppliers_wallet
        from apps.supplier_wallet.routes import supplier_wallet_bp
        if 'supplier_wallet_bp' not in app.blueprints:
            app.register_blueprint(supplier_wallet_bp, url_prefix='/supplier')
            print("✅ [Registry Supplier]: تم تسجيل موديول محفظة الموردين.")
        else:
            print("ℹ️ [Registry Supplier]: موديول محفظة الموردين مسجل مسبقاً.")
    except ImportError as e:
        print(f"❌ [Registry Supplier]: خطأ في استيراد routes: {e}")
    except Exception as e:
        print(f"❌ [Registry Supplier]: خطأ في تسجيل supplier_wallet: {e}")
    return app

def get_module_stats():
    try:
        from apps.models.wallet import SupplierWallet, WalletTransaction

        supplier_id = session.get('user_id') or session.get('supplier_id')
        user_type = session.get('user_type')

        if supplier_id and user_type != 'admin':
            wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
            balance = wallet.balance if wallet else 0.0
            pending_balance = wallet.pending_balance if hasattr(wallet, 'pending_balance') and wallet else 0.0
            
            transactions_count = WalletTransaction.query.filter_by(supplier_id=supplier_id).count()
        else:
            balance = 0.0
            pending_balance = 0.0
            transactions_count = 0

        stats = {
            'balance': balance,
            'pending_balance': pending_balance,
            'total_transactions': transactions_count,
            'has_wallet': True
        }
        return stats
    except Exception as e:
        print(f"❌ [Registry Supplier Wallet Stats Error]: {e}")
        return {'balance': 0.0, 'pending_balance': 0.0, 'total_transactions': 0, 'has_wallet': False}

def get_module_link():
    try:
        return url_for('supplier_wallet_bp.supplier_wallet_view')
    except Exception as e:
        print(f"❌ [Registry Supplier Wallet Link Error]: {e}")
        return '/supplier/wallet'

def get_dashboard_card():
    stats = get_module_stats()
    balance_formatted = f"{stats.get('balance', 0.0):,.2f}"
    return {
        'title': MODULE_NAME,
        'icon': MODULE_ICON,
        'link': get_module_link(),
        'stats': stats,
        'color': 'purple',
        'badge': f"{balance_formatted}",
        'subtitle': f"المعاملات: {stats.get('total_transactions', 0)}"
    }

__all__ = ['MODULE_NAME', 'MODULE_ICON', 'SHOW_IN_SUPPLIER', 'LINKS', 'register_module', 'get_module_stats', 'get_module_link', 'get_dashboard_card']
