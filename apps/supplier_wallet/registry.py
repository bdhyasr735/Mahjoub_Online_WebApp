# coding: utf-8
# 📂 apps/supplier_wallet/registry.py

import logging
from flask import url_for, session

logger = logging.getLogger(__name__)

MODULE_NAME = "المحفظة الرقمية"
MODULE_ICON = "fas fa-wallet"
SHOW_IN_SUPPLIER = True

LINKS = {
    "supplier_wallet_bp.transactions_redirect": "حركة المحفظة",
    "supplier_wallet_bp.withdraw_redirect": "سحب الرصيد"
}


def register_module(app):
    try:
        from apps.supplier_wallet.routes import supplier_wallet_bp
        if 'supplier_wallet_bp' not in app.blueprints:
            app.register_blueprint(supplier_wallet_bp)
            print("✅ [Registry Supplier Wallet]: تم تسجيل موديول المحفظة الرقمية.")
        else:
            print("ℹ️ [Registry Supplier Wallet]: موديول المحفظة الرقمية مسجل مسبقاً.")
    except ImportError as e:
        print(f"❌ [Registry Supplier Wallet]: خطأ في استيراد routes: {e}")
    except Exception as e:
        print(f"❌ [Registry Supplier Wallet]: خطأ في تسجيل supplier_wallet: {e}")
    return app


def get_module_stats():
    try:
        from apps.models.wallet_db import SupplierWallet, WalletTransaction, WithdrawalRequest

        supplier_id = session.get('user_id') or session.get('supplier_id')

        wallet = None
        if supplier_id:
            wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()

        if wallet:
            balance = float(getattr(wallet, 'balance', 0) or getattr(wallet, 'balance_sar', 0) or 0)
            pending_withdrawals = WithdrawalRequest.query.filter_by(wallet_id=wallet.id, status='pending').count()
            total_transactions = WalletTransaction.query.filter_by(wallet_id=wallet.id).count()
        else:
            balance = 0.0
            pending_withdrawals = 0
            total_transactions = 0

        return {
            'balance': balance,
            'pending_withdrawals': pending_withdrawals,
            'total_transactions': total_transactions,
            'has_wallet': wallet is not None
        }
    except Exception as e:
        print(f"❌ [Registry Supplier Wallet Stats Error]: {e}")
        return {'balance': 0.0, 'pending_withdrawals': 0, 'total_transactions': 0, 'has_wallet': False}


def get_module_link():
    try:
        return url_for('supplier_wallet_bp.transactions_redirect')
    except Exception as e:
        print(f"❌ [Registry Supplier Wallet Link Error]: {e}")
        # ✅ حل آمن: استخدام المسار المباشر لضمان ظهور الرابط دائماً
        return '/supplier/wallet/transactions'


def get_dashboard_card():
    stats = get_module_stats()
    return {
        'title': MODULE_NAME,
        'icon': MODULE_ICON,
        'link': get_module_link(),
        'stats': stats,
        'color': 'purple',
        'badge': f"{stats.get('balance', 0.0):,.2f} ر.س",
        'subtitle': f"{stats.get('pending_withdrawals', 0)} طلبات سحب معلقة"
    }


__all__ = ['MODULE_NAME', 'MODULE_ICON', 'SHOW_IN_SUPPLIER', 'LINKS', 'register_module', 'get_module_stats', 'get_module_link', 'get_dashboard_card']
