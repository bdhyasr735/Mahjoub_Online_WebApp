# coding: utf-8
"""
📂 apps/supplier_wallet/services/wallet_service.py
خدمات إدارة المحفظة والعمليات المالية للموردين
"""

from apps.models.wallet_db import SupplierWallet, WalletTransaction, WithdrawalRequest
from decimal import Decimal
import uuid

class WalletService:

    @staticmethod
    def get_or_create_wallet(session, supplier_id, trade_name="متجر المورد"):
        """جلب محفظة المورد أو إنشائها إذا لم تكن موجودة"""
        wallet = session.query(SupplierWallet).filter(SupplierWallet.supplier_id == supplier_id).first()
        
        if not wallet:
            wallet_code = f"WEL-{uuid.uuid4().hex[:6].upper()}"
            wallet = SupplierWallet(
                wallet_code=wallet_code,
                supplier_id=supplier_id,
                balance_sar=Decimal('0.00'),
                balance_pending=Decimal('0.00'),
                total_withdrawn=Decimal('0.00'),
                status='active'
            )
            session.add(wallet)
            session.flush()
            
        return wallet

    @staticmethod
    def create_withdrawal_request(session, wallet_id, bank_account, amount, notes=""):
        """إنشاء طلب سحب جديد وتحديث الأرصدة المعلقة في المحفظة بدون تعارض مع قيود القفل في بوستجرس"""
        # جلب المحفظة بالمعرف مباشرة بدون with_for_update لمنع أي Outer Join افتراضي مع الجداول المرتبطة
        wallet = session.query(SupplierWallet).filter(SupplierWallet.id == wallet_id).first()
        
        if not wallet:
            raise ValueError("المحفظة غير موجودة")
            
        if amount > wallet.balance_sar:
            raise ValueError("المبلغ المطلوب يتجاوز رصيد المحفظة المتاح")
            
        # خصم المبلغ من الرصيد المتاح وإضافته للرصيد المعلق
        wallet.balance_sar -= amount
        wallet.balance_pending = (wallet.balance_pending or Decimal('0.00')) + amount
        
        request_number = f"WDR-{uuid.uuid4().hex[:6].upper()}"
        
        withdrawal_request = WithdrawalRequest(
            request_number=request_number,
            wallet_id=wallet.id,
            amount=amount,
            bank_details=bank_account,
            status='pending',
            notes=notes
        )
        
        session.add(withdrawal_request)
        session.flush()
        
        return withdrawal_request
