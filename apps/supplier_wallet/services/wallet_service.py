# coding: utf-8
"""
📂 apps/supplier_wallet/services/wallet_service.py
منطق الأعمال المالي الحاسم (Atomic Financial Engine)
- عمليات محصنة داخل Transactions لمنع تعارض الأرصدة (Race Conditions & Deadlocks)
- إصدار أرقام السندات تلقائياً (VCH-YYYYMMDD-XXXX)
- تسجيل الحركة في دفتر الأستاذ (Immutable Ledger)
"""

from decimal import Decimal
import secrets
from datetime import datetime, timezone, timedelta
from apps.models.wallet_db import (
    SupplierWallet,
    WalletTransaction,
    WithdrawalRequest,
    WalletAuditLog,
    generate_voucher_number,
    get_mecca_now
)

# استيراد آمن لكلاس السندات لضمان عدم توقف السيرفر إذا لم يكن معرّفاً
try:
    from apps.models.wallet_db import VoucherReceipt
except ImportError:
    VoucherReceipt = None


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
                supplier_code=supplier_code,
                wallet_code=wallet_code,
                store_name=store_name,
                balance_sar=Decimal('0.00'),
                balance_pending=Decimal('0.00'),
                total_withdrawn=Decimal('0.00'),
                total_earned=Decimal('0.00')
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
        order_id: str = None,
        reference_number: str = None
    ) -> WalletTransaction:
        """
        إضافة رصيد مبيعات أو تعزيز مالي للمحفظة مع قفل القيد (Row Locking)
        """
        wallet = session.query(SupplierWallet).with_for_update().filter_by(id=wallet_id).first()
        if not wallet:
            raise ValueError("المحفظة غير موجودة")
        if not wallet.is_active or wallet.is_frozen:
            raise ValueError("المحفظة مجمدة أو غير نشطة")

        amount = Decimal(str(amount))
        if amount <= Decimal('0.00'):
            raise ValueError("مبلغ الإيداع يجب أن يكون أكبر من الصفر")

        # تحديث الأرصدة
        wallet.balance_sar += amount
        wallet.total_earned += amount
        wallet.updated_at = get_mecca_now()

        # إنشاء قيد الحركة المالية في دفتر الأستاذ
        voucher_num = generate_voucher_number()
        tx = WalletTransaction(
            wallet_id=wallet.id,
            voucher_number=voucher_num,
            reference_number=reference_number or f"DEP-{secrets.token_hex(4).upper()}",
            order_id=order_id,
            trans_type='deposit',
            amount=amount,
            fee_sar=Decimal('0.00'),
            net_amount=amount,
            balance_after=wallet.balance_sar,
            description=description,
            status='completed',
            created_at=get_mecca_now()
        )
        session.add(tx)
        session.flush()

        # إنشاء السند المحاسبي الرسمي إن وجد النموذج
        if VoucherReceipt:
            receipt = VoucherReceipt(
                wallet_id=wallet.id,
                transaction_id=tx.id,
                voucher_number=voucher_num,
                voucher_type='receipt',
                amount_words_ar=f"{amount:.2f} ريال سعودي لا غير",
                amount_sar=amount,
                created_at=get_mecca_now()
            )
            session.add(receipt)

        # تسجيل التدقيق الأمني
        audit = WalletAuditLog(
            wallet_id=wallet.id,
            action_type='DEPOSIT_REVENUE',
            actor_name='SYSTEM_AUTOMATION',
            changes_json={"amount": str(amount), "voucher": voucher_num, "balance_after": str(wallet.balance_sar)}
        )
        session.add(audit)

        return tx

    @staticmethod
    def create_withdrawal_request(
        session,
        wallet_id: int,
        bank_account_id: int,
        amount: Decimal,
        notes: str = None
    ) -> WithdrawalRequest:
        """
        طلب سحب رصيد: حجز المبلغ في الرصيد المعلق (Pending) وخصمه من المتاح
        """
        wallet = session.query(SupplierWallet).with_for_update().filter_by(id=wallet_id).first()
        if not wallet:
            raise ValueError("المحفظة غير موجودة")
        if not wallet.is_active or wallet.is_frozen:
            raise ValueError("المحفظة مجمدة أو غير نشطة")

        amount = Decimal(str(amount))
        if amount <= Decimal('0.00'):
            raise ValueError("مبلغ السحب يجب أن يكون أكبر من الصفر")
        if amount < Decimal('50.00'):
            raise ValueError("الحد الأدنى للسحب هو 50.00 ريال سعودي")
        if amount > wallet.balance_sar:
            raise ValueError("الرصيد المتاح غير كافٍ لإتمام طلب السحب")

        fee = Decimal('0.00')  # سحب مجاني بدون رسوم
        net_payout = amount - fee

        # حجز الرصيد
        wallet.balance_sar -= amount
        wallet.balance_pending += amount
        wallet.updated_at = get_mecca_now()

        req_number = f"WDR-{secrets.token_hex(4).upper()}"
        wdr = WithdrawalRequest(
            wallet_id=wallet.id,
            bank_account_id=bank_account_id,
            request_number=req_number,
            requested_amount=amount,
            fee_sar=fee,
            net_payout=net_payout,
            status='pending',
            supplier_notes=notes,
            created_at=get_mecca_now()
        )
        session.add(wdr)
        session.flush()

        audit = WalletAuditLog(
            wallet_id=wallet.id,
            action_type='WITHDRAWAL_REQUEST_CREATED',
            actor_name=wallet.store_name,
            changes_json={"amount": str(amount), "request_number": req_number}
        )
        session.add(audit)

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
        اعتماد وقبول طلب السحب من الإدارة: تحويل المبلغ من المعلق إلى المنفذ
        """
        wdr = session.query(WithdrawalRequest).with_for_update().filter_by(id=request_id).first()
        if not wdr or wdr.status != 'pending':
            raise ValueError("طلب السحب غير صالح أو تمت معالجته مسبقاً")

        wallet = session.query(SupplierWallet).with_for_update().filter_by(id=wdr.wallet_id).first()

        # تحرير الرصيد المعلق وزيادة إجمالي المسحوبات
        wallet.balance_pending -= wdr.requested_amount
        wallet.total_withdrawn += wdr.requested_amount
        wallet.updated_at = get_mecca_now()

        wdr.status = 'approved'
        wdr.approved_by = admin_name
        wdr.approved_at = get_mecca_now()
        wdr.admin_notes = notes

        # إنشاء قيد الصرف وسند الصرف
        voucher_num = generate_voucher_number()
        tx = WalletTransaction(
            wallet_id=wallet.id,
            voucher_number=voucher_num,
            reference_number=wdr.request_number,
            transfer_number=transfer_number or f"TRF-{secrets.token_hex(4).upper()}",
            approval_ref=f"APR-{secrets.token_hex(3).upper()}",
            trans_type='withdraw',
            amount=-wdr.requested_amount,
            fee_sar=wdr.fee_sar,
            net_amount=-wdr.net_payout,
            balance_after=wallet.balance_sar,
            description=f"تحويل أرباح ومستحقات بنكية إلى الحساب المعتمد ({notes or 'تمت الموافقة بنجاح'})",
            status='completed',
            bank_account_id=wdr.bank_account_id,
            created_at=get_mecca_now()
        )
        session.add(tx)
        session.flush()

        if VoucherReceipt:
            receipt = VoucherReceipt(
                wallet_id=wallet.id,
                transaction_id=tx.id,
                voucher_number=voucher_num,
                voucher_type='payment',
                amount_words_ar=f"{wdr.requested_amount:.2f} ريال سعودي لا غير",
                amount_sar=wdr.requested_amount,
                created_at=get_mecca_now()
            )
            session.add(receipt)

        audit = WalletAuditLog(
            wallet_id=wallet.id,
            action_type='WITHDRAWAL_APPROVED',
            actor_name=admin_name,
            changes_json={"amount": str(wdr.requested_amount), "voucher": voucher_num}
        )
        session.add(audit)

        return tx

    @staticmethod
    def reject_withdrawal(
        session,
        request_id: int,
        admin_name: str,
        reason: str = None
    ) -> WithdrawalRequest:
        """
        رفض طلب السحب وإلغاء حجز المبلغ وإعادته للرصيد المتاح بالمحفظة
        """
        wdr = session.query(WithdrawalRequest).with_for_update().filter_by(id=request_id).first()
        if not wdr or wdr.status != 'pending':
            raise ValueError("طلب السحب غير صالح أو تمت معالجته مسبقاً")

        wallet = session.query(SupplierWallet).with_for_update().filter_by(id=wdr.wallet_id).first()

        # إعادة خصم المعلق وإضافته مجدداً للرصيد المتاح
        wallet.balance_pending -= wdr.requested_amount
        wallet.balance_sar += wdr.requested_amount
        wallet.updated_at = get_mecca_now()

        wdr.status = 'rejected'
        wdr.approved_by = admin_name
        wdr.approved_at = get_mecca_now()
        wdr.admin_notes = reason or 'تم رفض طلب السحب من الإدارة'

        audit = WalletAuditLog(
            wallet_id=wallet.id,
            action_type='WITHDRAWAL_REJECTED',
            actor_name=admin_name,
            changes_json={"amount": str(wdr.requested_amount), "reason": reason}
        )
        session.add(audit)

        return wdr
