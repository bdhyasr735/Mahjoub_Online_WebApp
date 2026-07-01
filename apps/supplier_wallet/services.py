# coding: utf-8
# 📂 apps/supplier_wallet/services.py

from apps.models.wallet_db import SupplierWallet, WalletTransaction

class WalletService:
    @staticmethod
    def get_supplier_wallet_data(supplier_id, currency='SAR'):
        """جلب محفظة المورد وحركاته المالية المفلترة."""
        wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
        transactions = []
        if wallet:
            transactions = WalletTransaction.query.filter_by(
                wallet_id=wallet.id, 
                currency=currency
            ).order_by(WalletTransaction.created_at.desc()).all()
        return wallet, transactions
