# coding: utf-8
"""
📂 apps/supplier_wallet/services/wallet_service.py
منطق الأعمال المالي الحاسم (Atomic Financial Engine)
- عمليات محصنة داخل Transactions لمنع تعارض الأرصدة (Race Conditions & Deadlocks)
- إصدار أرقام السندات والعمليات تلقائياً
- تسجيل الحركة في دفتر الأستاذ والمحفظة
"""

from decimal import Decimal
import secrets
from datetime import datetime, timezone, timedelta
from apps.models.wallet_db import (
    SupplierWallet,
    WalletTransaction,
    WithdrawalRequest
)


def get_mecca_now():
    """الحصول على توقيت مكة المكرمة الحالي"""
    return datetime.now(timezone(timedelta(hours=3)))


class WalletService:
    """
    محرك العمليات المالية والتدقيق المحاسبي لمحفظة محجوب أونلاين
    """

    @staticmethod
    def get_or_create_wallet(session, supplier_id: int, store_name: str, supplier_code: str = None) -> SupplierWallet:
        """جلب المحفظة أو إنشاؤها فورياً برقم تسلسلي موحد"""
        wallet = session.query(SupplierWallet).filter_by(supplier_id=supplier_id).first()
        if not wallet:
            if not supplier_code:
                supplier_code = f"SUP-{supplier_id}"
            wallet_code = supplier_code.replace("SUP-", "WEL-")
            wallet = SupplierWallet(
                supplier_id=supplier_id,
                wallet_code=wallet_code,
                status='active',
                balance_sar=Decimal('0.00'),
                balance_pending=Decimal('0.00'),
                total_withdrawn=Decimal('0.00')
            )
            session.add(wallet)
            session.flush()
        return wallet

    @staticmethod
    def deposit_revenue(
        session,
        wallet_id: int,
        amount: Decimal,
        description: str,
        currency: str = 'SAR',
        reference_number: str = None
    ) -> WalletTransaction:
        """
        إضافة رصيد مبيعات أو تعزيز مالي للمحفظة
        """
        wallet = session.query(SupplierWallet).with_for_update().filter_by(id=wallet_id).first()
        if not wallet:
            raise ValueError("المحفظة غير موجودة")
        if wallet.status != 'active':
            raise ValueError("المحفظة غير نشطة أو مجمدة")

        amount = Decimal(str(amount))
        if amount <= Decimal('0.00'):
            raise ValueError("مبلغ الإيداع يجب أن يكون أكبر من الصفر")

        # إنشاء قيد الحركة المالية (الـ Model يتكفل بتحديث الرصيد وتوليد الأرقام عبر الـ Event)
        tx = WalletTransaction(
            wallet_id=wallet.id,
            trans_type='deposit',
            amount=amount,
            currency=currency,
            reference_number=reference_number,
            description=description,
            status='completed',
            created_at=get_mecca_now()
        )
        session.add(tx)
        session.flush()

        return tx

    @staticmethod
    def create_withdrawal_request(
        session,
        wallet_id: int,
        bank_account_id: str,
        amount: Decimal,
        notes: str = None
    ) -> WithdrawalRequest:
        """
        طلب سحب رصيد: التحقق من الرصيد وإنشاء الطلب بحالة معلقة دون خصم فوري من الرصيد المتاح
        """
        wallet = session.query(SupplierWallet).with_for_update().filter_by(id=wallet_id).first()
        if not wallet:
            raise ValueError("المحفظة غير موجودة")
        if wallet.status != 'active':
            raise ValueError("المحفظة غير نشطة أو مجمدة")

        amount = Decimal(str(amount))
        if amount <= Decimal('0.00'):
            raise ValueError("مبلغ السحب يجب أن يكون أكبر من الصفر")
        if amount < Decimal('50.00'):
            raise ValueError("الحد الأدنى للسحب هو 50.00 ريال سعودي")
        if amount > wallet.balance_sar:
            raise ValueError("الرصيد المتاح غير كافٍ لإتمام طلب السحب")

        # لا يتم خصم المبلغ من الرصيد المتاح هنا، بل يتم التحقق وتسجيل الطلب كمعلق فقط
        req_number = f"WDR-{secrets.token_hex(4).upper()}"
        wdr = WithdrawalRequest(
            request_number=req_number,
            supplier_id=wallet.supplier_id,
            wallet_id=wallet.id,
            amount=amount,
            currency='SAR',
            payout_method=str(bank_account_id),
            status='pending',
            notes=notes,
            created_at=get_mecca_now()
        )
        session.add(wdr)
        session.flush()

        return wdr

    @staticmethod
    def approve_withdrawal(
        session,
        request_id: int,
        admin_name: str,
        transfer_number: str = None,
        notes: str = None
    ) -> WalletTransaction:
        """
        اعتماد وقبول طلب السحب من الإدارة (يتم خصم المبلغ من الرصيد المتاح وتسجيل سند الصرف نهائياً)
        """
        wdr = session.query(WithdrawalRequest).with_for_update().filter_by(id=request_id).first()
        if not wdr or wdr.status != 'pending':
            raise ValueError("طلب السحب غير صالح أو تمت معالجته مسبقاً")

        wallet = session.query(SupplierWallet).with_for_update().filter_by(id=wdr.wallet_id).first()
        if wallet.balance_sar < wdr.amount:
            raise ValueError("رصيد المورد المتاح لم يعد كافياً لتنفيذ عملية الصرف")

        # خصم المبلغ من الرصيد المتاح وإضافته للمسحوبات نهائياً عند الموافقة
        wallet.balance_sar -= wdr.amount
        wallet.total_withdrawn += wdr.amount
        wallet.updated_at = get_mecca_now()

        wdr.status = 'approved'
        wdr.updated_at = get_mecca_now()

        # إنشاء قيد خصم (صرف) في الحركات المالية
        tx = WalletTransaction(
            wallet_id=wallet.id,
            trans_type='withdraw',
            amount=wdr.amount,
            currency=wdr.currency,
            transfer_number=transfer_number or f"TRF-{secrets.token_hex(4).upper()}",
            payout_bank=wdr.payout_method,
            approval_ref=f"APR-{admin_name}",
            description=f"صرف طلب سحب أرباح رقم {wdr.request_number} ({notes or 'تمت الموافقة'})",
            status='completed',
            created_at=get_mecca_now()
        )
        session.add(tx)
        session.flush()

        return tx

    @staticmethod
    def reject_withdrawal(
        session,
        request_id: int,
        admin_name: str,
        reason: str = None
    ) -> WithdrawalRequest:
        """
        رفض طلب السحب (بما أن الرصيد لم يُخصم مسبقاً، يتم فقط تحديث حالة الطلب إلى مرفوض وتثبيت السبب)
        """
        wdr = session.query(WithdrawalRequest).with_for_update().filter_by(id=request_id).first()
        if not wdr or wdr.status != 'pending':
            raise ValueError("طلب السحب غير صالح أو تمت معالجته مسبقاً")

        # لا داعي لتعديل الأرصدة لأننا لم نقوم بتجميدها أو خصمها لحظة إنشاء الطلب
        wdr.status = 'rejected'
        wdr.notes = f"{wdr.notes or ''} | سبب الرفض من ({admin_name}): {reason or 'غير محدد'}"
        wdr.updated_at = get_mecca_now()

        return wdr
