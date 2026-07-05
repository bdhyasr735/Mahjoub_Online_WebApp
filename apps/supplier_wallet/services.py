# coding: utf-8
# 📂 apps/supplier_wallet/services.py

from apps.models.wallet_db import SupplierWallet, WalletTransaction
from sqlalchemy import func

class WalletService:
    @staticmethod
    def get_wallet_summary(supplier_id, currency='SAR'):
        """جلب المحفظة، الحركات، وحساب الإجماليات في عملية واحدة."""
        wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
        
        if not wallet:
            return None, [], 0, 0
            
        # جلب الحركات الأساسية
        query = WalletTransaction.query.filter_by(wallet_id=wallet.id, currency=currency)
        transactions = query.order_by(WalletTransaction.created_at.desc()).all()
        
        # حساب الإجماليات (محسنة لتكون جزءاً من الخدمة)
        stats = query.with_entities(
            func.sum(WalletTransaction.amount).filter(
                WalletTransaction.trans_type.in_(['credit', 'adjustment_credit', 'sale_revenue'])
            ).label('total_credit'),
            func.sum(WalletTransaction.amount).filter(
                WalletTransaction.trans_type.in_(['withdrawal', 'adjustment_debit'])
            ).label('total_debit')
        ).first()
        
        return wallet, transactions, (stats.total_credit or 0), (stats.total_debit or 0)
