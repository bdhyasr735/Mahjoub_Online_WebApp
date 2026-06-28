# coding: utf-8
# 📂 apps/supplier_wallet/services.py

# تم تعديل الاستيراد ليكون من المجلد الرئيسي للموديلات لضمان استقرار العلاقات وقابلية التوسع
from apps.models import SupplierWallet, WalletTransaction
from apps.extensions import db

class WalletService:
    @staticmethod
    def get_supplier_wallet(supplier_id):
        """جلب محفظة المورد بناءً على معرف المورد"""
        return SupplierWallet.query.filter_by(supplier_id=supplier_id).first()

    @staticmethod
    def process_transaction(supplier_id, amount, trans_type, currency, description, reference_number):
        """
        خدمة معالجة الحركة المالية للمورد
        تضمن تحديث الرصيد وتسجيل القيد في آن واحد كعملية موحدة (Atomic Operation)
        """
        wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
        if not wallet:
            raise ValueError("المحفظة غير موجودة")

        # تحديث الأرصدة بناءً على نوع العملة ونوع الحركة المالية
        if currency == 'SAR':
            wallet.balance_sar += amount if trans_type == 'credit' else -amount
        elif currency == 'YER':
            wallet.balance_yer += amount if trans_type == 'credit' else -amount
        elif currency == 'USD':
            wallet.balance_usd += amount if trans_type == 'credit' else -amount
        else:
            raise ValueError(f"العملة {currency} غير مدعومة في النظام حالياً")

        # تسجيل القيد في جدول حركات المحفظة
        transaction = WalletTransaction(
            wallet_id=wallet.id,
            trans_type=trans_type,
            source_type='manual_adjustment',
            amount=amount,
            currency=currency,
            description=description,
            reference_number=reference_number
        )
        
        db.session.add(transaction)
        db.session.commit()
        return transaction

    @staticmethod
    def get_balance_summary(wallet):
        """تجهيز ملخص الأرصدة لعرضه في لوحة الموردين"""
        return {
            'SAR': wallet.balance_sar,
            'YER': wallet.balance_yer,
            'USD': wallet.balance_usd
        }
