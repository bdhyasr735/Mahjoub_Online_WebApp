# coding: utf-8
"""
📂 apps/supplier_wallet/services/wallet_service.py
خدمات إدارة المحفظة والعمليات المالية للموردين
"""

import uuid
import secrets
import string
from decimal import Decimal
from apps.models.wallet_db import SupplierWallet, WalletTransaction, WithdrawalRequest

class WalletService:

    @staticmethod
    def _get_balance_attr_name(wallet_or_cls):
        """تحديد اسم حقل الرصيد الرئيسي في الكائن أو الكلاس بشكل ديناميكي."""
        for attr in ['balance_sar', 'balance', 'wallet_balance', 'amount']:
            if hasattr(wallet_or_cls, attr):
                return attr
        return 'balance'

    @staticmethod
    def _get_pending_attr_name(wallet_or_cls):
        """تحديد اسم حقل الرصيد المعلق في الكائن أو الكلاس بشكل ديناميكي."""
        for attr in ['balance_pending', 'pending_balance']:
            if hasattr(wallet_or_cls, attr):
                return attr
        return None

    @classmethod
    def get_or_create_wallet(cls, session, supplier_id, trade_name="متجر المورد"):
        """جلب محفظة المورد أو إنشائها إذا لم تكن موجودة"""
        wallet = session.query(SupplierWallet).filter(SupplierWallet.supplier_id == supplier_id).first()
        
        if not wallet:
            wallet_code = f"WEL-{uuid.uuid4().hex[:6].upper()}"
            
            kwargs = {
                'supplier_id': supplier_id,
                'status': 'active'
            }
            if hasattr(SupplierWallet, 'wallet_code'):
                kwargs['wallet_code'] = wallet_code

            # تعيين الرصيد الأساسي حسب الحقل المتوفر في النموذج
            bal_attr = cls._get_balance_attr_name(SupplierWallet)
            kwargs[bal_attr] = Decimal('0.00')

            # تعيين الرصيد المعلق إذا كان الحقل موجوداً
            pending_attr = cls._get_pending_attr_name(SupplierWallet)
            if pending_attr:
                kwargs[pending_attr] = Decimal('0.00')

            if hasattr(SupplierWallet, 'total_withdrawn'):
                kwargs['total_withdrawn'] = Decimal('0.00')

            wallet = SupplierWallet(**kwargs)
            session.add(wallet)
            session.flush()
            
        return wallet

    @classmethod
    def create_withdrawal_request(cls, session, wallet_id, bank_account, amount, notes=""):
        """إنشاء طلب سحب جديد وتحديث الأرصدة المعلقة في المحفظة بدون تعارض مع قيود القفل في بوستجرس"""
        wallet = session.query(SupplierWallet).filter(SupplierWallet.id == wallet_id).first()
        
        if not wallet:
            raise ValueError("المحفظة غير موجودة")

        amount_decimal = Decimal(str(amount))

        # جلب اسم حقل الرصيد المتوفر وقيمته الحالية
        bal_attr = cls._get_balance_attr_name(wallet)
        raw_balance = getattr(wallet, bal_attr, Decimal('0.00'))
        current_balance = Decimal(str(raw_balance)) if raw_balance is not None else Decimal('0.00')

        if amount_decimal > current_balance:
            raise ValueError(f"المبلغ المطلوب ({amount_decimal:.2f} ر.س) يتجاوز رصيد المحفظة المتاح ({current_balance:.2f} ر.س)")

        # خصم المبلغ من الرصيد المتاح
        setattr(wallet, bal_attr, current_balance - amount_decimal)

        # إضافته للرصيد المعلق إذا كان الحقل موجوداً في النموذج
        pending_attr = cls._get_pending_attr_name(wallet)
        if pending_attr:
            raw_pending = getattr(wallet, pending_attr, Decimal('0.00'))
            current_pending = Decimal(str(raw_pending)) if raw_pending is not None else Decimal('0.00')
            setattr(wallet, pending_attr, current_pending + amount_decimal)

        # توليد رقم طلب سحب فريد مطابق تماماً للنمط الرسمي المعتمد WDR-MAH-
        characters = string.ascii_uppercase + string.digits
        while True:
            random_str = ''.join(secrets.choice(characters) for _ in range(6))
            candidate_number = f"WDR-MAH-{random_str}"
            existing = session.query(WithdrawalRequest).filter_by(request_number=candidate_number).first()
            if not existing:
                request_number = candidate_number
                break

        # استخدام العمود الصريح والمدعوم في النموذج WithdrawalRequest وهو payout_method مع تمرير supplier_id
        withdrawal_request = WithdrawalRequest(
            request_number=request_number,
            supplier_id=wallet.supplier_id,
            wallet_id=wallet.id,
            amount=amount_decimal,
            payout_method=bank_account,
            status='pending',
            notes=notes
        )
        
        session.add(withdrawal_request)
        session.flush()
        
        return withdrawal_request
