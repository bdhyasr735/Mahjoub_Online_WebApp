# -*- coding: utf-8 -*-
# 📂 apps/models/wallet_db.py

import os
import random
import string
from datetime import datetime
from cryptography.fernet import Fernet
from sqlalchemy import event, update
from apps.extensions import db


def _get_encryption_key():
    """جلب مفتاح التشفير السيادي الخاص بالمنصة"""
    key = os.environ.get('ENCRYPTION_KEY')
    return key.encode() if key else b'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8Vq='


def generate_unique_voucher_number():
    """توليد رقم سند فريد بالبادئة VCH-MAH متبوعة بـ 6 أرقام عشوائية مع ضمان عدم التكرار"""
    while True:
        random_digits = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        voucher_code = f"VCH-MAH{random_digits}"
        exists = WalletTransaction.query.filter_by(voucher_number=voucher_code).first()
        if not exists:
            return voucher_code


class SupplierWallet(db.Model):
    """نموذج المحفظة المالية الذكية للموردين - يدعم الترقيم النمطي WEL-963X والفهرسة المتقدمة"""
    __tablename__ = 'supplier_wallets'

    # [فهرسة متقدمة]: لضمان أقصى سرعة في استعلامات الأرصدة والتقارير المالية
    __table_args__ = (
        db.Index('idx_wallet_code', 'wallet_code'),
        db.Index('idx_wallet_supplier_id', 'supplier_id'),
        db.Index('idx_wallet_status', 'is_active'),
        db.Index('idx_wallet_created', 'created_at'),
        {'extend_existing': True}
    )

    # المعرفات الأساسية والأرصدة
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id', ondelete='CASCADE'), nullable=False, unique=True)
    wallet_code = db.Column(db.String(50), unique=True, nullable=True)

    balance = db.Column(db.Numeric(12, 2), default=0.00, nullable=False)
    balance_pending = db.Column(db.Numeric(12, 2), default=0.00, nullable=False)
    total_withdrawn = db.Column(db.Numeric(12, 2), default=0.00, nullable=False)
    currency = db.Column(db.String(10), default='SAR', nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقات: التحميل الكسول (lazy='select')
    supplier = db.relationship('Supplier', back_populates='wallet', uselist=False, lazy='select')
    transactions = db.relationship('WalletTransaction', back_populates='wallet', lazy='select', cascade="all, delete-orphan")
    withdrawal_requests = db.relationship('WithdrawalRequest', back_populates='wallet', lazy='select', cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        kwargs['currency'] = 'SAR'
        super().__init__(**kwargs)

    # --- Properties للتوافق المرن والآمن مع الخدمات والمكونات المختلفة ---
    @property
    def balance_sar(self):
        """خاصية للتوافق مع الخدمات التي تعتمد مسمى balance_sar"""
        return self.balance

    @balance_sar.setter
    def balance_sar(self, value):
        self.balance = value

    def to_dict(self):
        return {
            'id': self.id,
            'supplier_id': self.supplier_id,
            'wallet_code': self.wallet_code,
            'balance': float(self.balance) if self.balance is not None else 0.00,
            'balance_pending': float(self.balance_pending) if self.balance_pending is not None else 0.00,
            'total_withdrawn': float(self.total_withdrawn) if self.total_withdrawn is not None else 0.00,
            'currency': self.currency,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f"<SupplierWallet {self.wallet_code or self.id}: {self.balance} {self.currency}>"


class WalletTransaction(db.Model):
    """نموذج حركات المحفظة المالية - يدعم التشفير السيادي للوصف والفهرسة المتقدمة"""
    __tablename__ = 'wallet_transactions'

    # [فهرسة متقدمة]: لضمان السرعة العالية في مطابقة قيود الحركات المالية
    __table_args__ = (
        db.Index('idx_txn_wallet_id', 'wallet_id'),
        db.Index('idx_txn_voucher', 'voucher_number'),
        db.Index('idx_txn_type', 'transaction_type'),
        db.Index('idx_txn_status', 'status'),
        db.Index('idx_txn_created', 'created_at'),
        {'extend_existing': True}
    )

    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('supplier_wallets.id', ondelete='CASCADE'), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)
    voucher_number = db.Column(db.String(100), unique=True, nullable=True, index=True)

    # ✅ [حقول جديدة]: لتخزين المرجع البنكي وشركة التحويل
    bank_reference = db.Column(db.String(255), nullable=True)
    transfer_company = db.Column(db.String(255), nullable=True)

    # ✅ [حقل جديد]: حالة الحركة (مكتملة / معلقة / ملغاة)
    status = db.Column(db.String(20), default='completed', nullable=False)

    # [التشفير السيادي]: وصف الحركة المالية مشفر بالكامل في قاعدة البيانات
    _description_enc = db.Column(db.String(500), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    wallet = db.relationship('SupplierWallet', back_populates='transactions', lazy='select')
    
    # ✅ [علاقة جديدة]: ربط الحركة بالبيانات المالية للطلبات (يظهر في سجل الخزينة)
    financials = db.relationship('OrderFinancial', back_populates='transaction', lazy='select')

    def __init__(self, **kwargs):
        desc_val = kwargs.pop('description', None)
        super().__init__(**kwargs)
        if desc_val is not None:
            self.description = desc_val

    # --- نظام التشفير السيادي لوصف الحركة المالية ---
    def _encrypt(self, value):
        if not value:
            return ""
        f = Fernet(_get_encryption_key())
        return f.encrypt(str(value).encode()).decode()

    def _decrypt(self, value):
        if not value:
            return ""
        try:
            f = Fernet(_get_encryption_key())
            return f.decrypt(value.encode()).decode()
        except Exception:
            return value or ""

    @property
    def description(self):
        return self._decrypt(self._description_enc)

    @description.setter
    def description(self, value):
        if value:
            self._description_enc = self._encrypt(value)
        else:
            self._description_enc = None

    def to_dict(self):
        return {
            'id': self.id,
            'wallet_id': self.wallet_id,
            'amount': float(self.amount) if self.amount is not None else 0.00,
            'transaction_type': self.transaction_type,
            'voucher_number': self.voucher_number,
            'status': self.status,
            'bank_reference': self.bank_reference,
            'transfer_company': self.transfer_company,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<WalletTransaction {self.id}: {self.transaction_type} {self.amount} | Status: {self.status}>"


class WithdrawalRequest(db.Model):
    """نموذج طلبات سحب الأرباح - يدعم التشفير السيادي للبيانات البنكية والفهرسة المتقدمة"""
    __tablename__ = 'withdrawal_requests'

    # [فهرسة متقدمة]: لسرعة الاستعلام المالي وتدقيق طلبات السحب
    __table_args__ = (
        db.Index('idx_withdrawal_wallet_id', 'wallet_id'),
        db.Index('idx_withdrawal_request_number', 'request_number'),
        db.Index('idx_withdrawal_supplier_id', 'supplier_id'),
        db.Index('idx_withdrawal_status', 'status'),
        db.Index('idx_withdrawal_created', 'created_at'),
        {'extend_existing': True}
    )

    id = db.Column(db.Integer, primary_key=True)
    request_number = db.Column(db.String(100), unique=True, nullable=True, index=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id', ondelete='CASCADE'), nullable=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('supplier_wallets.id', ondelete='CASCADE'), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)

    # [التشفير السيادي]: تفاصيل الحساب البنكي ووسيلة التحويل مشفرة بالكامل
    _payout_method_enc = db.Column(db.String(500), nullable=True)

    status = db.Column(db.String(50), default='pending', nullable=False)
    notes = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    wallet = db.relationship('SupplierWallet', back_populates='withdrawal_requests', lazy='select')

    def __init__(self, **kwargs):
        payout_val = kwargs.pop('payout_method', None)
        super().__init__(**kwargs)
        if payout_val is not None:
            self.payout_method = payout_val

    # --- نظام التشفير السيادي للحسابات والآيبان البنكي ---
    def _encrypt(self, value):
        if not value:
            return ""
        f = Fernet(_get_encryption_key())
        return f.encrypt(str(value).encode()).decode()

    def _decrypt(self, value):
        if not value:
            return ""
        try:
            f = Fernet(_get_encryption_key())
            return f.decrypt(value.encode()).decode()
        except Exception:
            return value or ""

    @property
    def payout_method(self):
        return self._decrypt(self._payout_method_enc)

    @payout_method.setter
    def payout_method(self, value):
        if value:
            self._payout_method_enc = self._encrypt(value)
        else:
            self._payout_method_enc = None

    def to_dict(self):
        return {
            'id': self.id,
            'request_number': self.request_number,
            'supplier_id': self.supplier_id,
            'wallet_id': self.wallet_id,
            'amount': float(self.amount) if self.amount is not None else 0.00,
            'payout_method': self.payout_method,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f"<WithdrawalRequest {self.request_number or self.id}: {self.amount} - {self.status}>"


# --- المحرك التلقائي لضمان كود النمط الفريد WDR-MAH لطلبات السحب تلقائياً ---
@event.listens_for(WithdrawalRequest, 'after_insert')
def receive_after_insert_withdrawal(mapper, connection, target):
    """توليد رقم طلب السحب (WDR-MAH-XXXX) تلقائياً عند إنشاء السجل إن لم يتم تمريره"""
    if not target.request_number:
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        generated_code = f"WDR-MAH-{random_str}"
        connection.execute(
            update(WithdrawalRequest).where(WithdrawalRequest.id == target.id).values(request_number=generated_code)
        )


# --- [إضافة جديدة] المحرك التلقائي لضمان كود النمط الفريد VCH-MAH لعمليات المحفظة تلقائياً ---
@event.listens_for(WalletTransaction, 'after_insert')
def receive_after_insert_wallet_txn(mapper, connection, target):
    """توليد رقم سند (VCH-MAH) تلقائياً عند إنشاء معاملة المحفظة إن لم يتم تمريره"""
    if not target.voucher_number:
        # استدعاء الدالة الموجودة بالأعلى لتوليد الرقم
        generated_code = generate_unique_voucher_number()
        # تحديث السجل مباشرة في قاعدة البيانات
        connection.execute(
            update(WalletTransaction).where(WalletTransaction.id == target.id).values(voucher_number=generated_code)
        )
