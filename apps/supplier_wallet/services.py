# coding: utf-8
# 📂 apps/supplier_wallet/services.py (مُعدل ومجهز)

from decimal import Decimal, InvalidOperation
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from apps.extensions import db
import logging

logger = logging.getLogger(__name__)

class WalletService:
    @staticmethod
    def get_supplier_wallet(supplier_id):
        return SupplierWallet.query.filter_by(supplier_id=supplier_id).first()

    @staticmethod
    def process_transaction(supplier_id, amount, trans_type, currency, description, reference_number, source_type='manual_adjustment'):
        """معالجة الحركات المالية وتحديث الخزنة"""
        wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
        if not wallet:
            raise ValueError(f"المحفظة غير موجودة للمورد رقم {supplier_id}")

        # تحويل المبلغ إلى Decimal لضمان الدقة الحسابية الصارمة
        try:
            decimal_amount = Decimal(str(amount))
        except (InvalidOperation, ValueError):
            logger.error(f"خطأ في تنسيق المبلغ للمورد {supplier_id}: {amount}")
            decimal_amount = Decimal('0.00')

        # إنشاء قيد الحركة المالية
        transaction = WalletTransaction(
            wallet_id=wallet.id,
            trans_type=trans_type, # credit (إيداع) أو debit (سحب)
            source_type=source_type,
            amount=decimal_amount,
            currency=currency,
            description=description,
            reference_number=reference_number,
            owner_id=supplier_id 
        )
        
        db.session.add(transaction)
        # سيقوم Event Listener في نموذج المحفظة بتحديث الرصيد التراكمي تلقائياً عند الـ commit
        db.session.commit() 
        return transaction

    @staticmethod
    def sync_order_payment(supplier_id, order_id, amount, currency='SAR'):
        """المحرك المالي لتسوية الطلبات التلقائية"""
        # نستخدم reference_number لمنع التكرار (Idempotency)
        ref_num = f"QMR-{order_id}"
        
        # التأكد من عدم وجود تسوية سابقة لنفس الطلب
        existing = WalletTransaction.query.filter_by(reference_number=ref_num).first()
        if existing:
            logger.warning(f"محاولة تسوية مكررة للطلب {order_id}. تم الإلغاء.")
            return existing

        return WalletService.process_transaction(
            supplier_id=supplier_id,
            amount=amount, 
            trans_type='credit',
            currency=currency,
            description=f"تسوية مالية تلقائية للطلب رقم {order_id}",
            reference_number=ref_num,
            source_type='system_sync'
        )
