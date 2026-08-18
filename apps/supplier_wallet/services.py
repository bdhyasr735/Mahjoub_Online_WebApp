# coding: utf-8
# 📂 apps/supplier_wallet/services.py

from apps.models.wallet_db import SupplierWallet, WalletTransaction
from sqlalchemy import func
from decimal import Decimal
from apps.extensions import db
from apps.supplier_wallet.utils import generate_transaction_ref

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
        
        # حساب الإجماليات
        stats = query.with_entities(
            func.sum(WalletTransaction.amount).filter(
                WalletTransaction.trans_type.in_(['credit', 'adjustment_credit', 'sale_revenue'])
            ).label('total_credit'),
            func.sum(WalletTransaction.amount).filter(
                WalletTransaction.trans_type.in_(['withdrawal', 'adjustment_debit'])
            ).label('total_debit')
        ).first()
        
        return wallet, transactions, (stats.total_credit or 0), (stats.total_debit or 0)

    @staticmethod
    def process_withdrawal(supplier_id: int, amount: Decimal, description: str = "سحب أرباح المورد"):
        """تنفيذ عملية سحب أرباح وإدارة المعاملات المالية."""
        wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
        if not wallet or wallet.balance_sar < amount:
            return False, "رصيد غير كافٍ أو محفظة غير موجودة."

        # توليد مراجع المعاملة
        ref, vch = generate_transaction_ref(wallet.id, wallet.wallet_code.split('-')[-1])
        
        try:
            # 1. إنشاء سجل المعاملة
            transaction = WalletTransaction(
                wallet_id=wallet.id,
                amount=amount,
                trans_type='withdrawal',
                status='pending',
                description=description,
                reference_number=ref,
                voucher_number=vch,
                currency=wallet.default_currency or 'SAR'
            )
            
            # 2. تحديث أرصدة المحفظة
            wallet.balance_sar -= amount
            wallet.balance_pending += amount
            
            db.session.add(transaction)
            db.session.commit()
            return True, "تم تقديم طلب السحب بنجاح بانتظار المراجعة."
        except Exception as e:
            db.session.rollback()
            return False, f"حدث خطأ أثناء معالجة الطلب: {str(e)}"
