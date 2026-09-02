# -*- coding: utf-8 -*-
# 📂 apps/models/wallet_db.py

import random
from datetime import datetime
from apps.extensions import db


def generate_unique_voucher_number():
    """توليد رقم سند فريد بالبادئة VCH-MAH متبوعة بـ 6 أرقام عشوائية مع ضمان عدم التكرار"""
    while True:
        random_digits = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        voucher_code = f"VCH-MAH{random_digits}"
        
        # التحقق من عدم وجود الكود مسبقاً في قاعدة البيانات (في جدول الحركات أو نموذج يعتمد عليه)
        exists = WalletTransaction.query.filter_by(description=voucher_code).first() # أو التحقق حسب الجدول المرتبط
        if not exists:
            return voucher_code


class SupplierWallet(db.Model):
    """نموذج المحفظة المالية الذكية للموردين - يدعم الترقيم النمطي WEL-963X والعملة بالريال السعودي فقط"""
    __tablename__ = 'supplier_wallets'

    # [فهرسة متقدمة]: لسرعة الاستعلامات والبحث
    __table_args__ = (
        db.Index('idx_wallet_code', 'wallet_code'),
        db.Index('idx_wallet_supplier_id', 'supplier_id'),
        db.Index('idx_wallet_status', 'is_active'),
        {'extend_existing': True}
    )

    # المعرفات الأساسية
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id', ondelete='CASCADE'), nullable=False, unique=True)
    wallet_code = db.Column(db.String(50), unique=True, nullable=True)  # الترقيم النمطي مثل WEL-9631
    
    # تفاصيل الحساب المالي (العملة ريال سعودي SAR حصراً)
    balance = db.Column(db.Numeric(12, 2), default=0.00, nullable=False)
    currency = db.Column(db.String(10), default='SAR', nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # تواريخ المتابعة
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقات (تحميل كسول lazy='select' وتجنب الاستيراد الدائري)
    supplier = db.relationship('Supplier', back_populates='wallet', uselist=False, lazy='select')
    transactions = db.relationship('WalletTransaction', back_populates='wallet', lazy='select', cascade="all, delete-orphan")
    withdrawal_requests = db.relationship('WithdrawalRequest', back_populates='wallet', lazy='select', cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        """تثبيت العملة حصراً على الريال السعودي SAR بغض النظر عن المدخلات"""
        kwargs['currency'] = 'SAR'
        super().__init__(**kwargs)

    def to_dict(self):
        """تحويل المحفظة إلى قاموس آمن للاستخدام في APIs"""
        return {
            'id': self.id,
            'supplier_id': self.supplier_id,
            'wallet_code': self.wallet_code,
            'balance': float(self.balance) if self.balance is not None else 0.00,
            'currency': self.currency,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f"<SupplierWallet {self.wallet_code or self.id}: {self.balance} {self.currency}>"


class WalletTransaction(db.Model):
    """نموذج حركات المحفظة المالية"""
    __tablename__ = 'wallet_transactions'

    __table_args__ = (
        db.Index('idx_txn_wallet_id', 'wallet_id'),
        db.Index('idx_txn_created', 'created_at'),
        {'extend_existing': True}
    )

    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('supplier_wallets.id', ondelete='CASCADE'), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)  # credit, debit
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    wallet = db.relationship('SupplierWallet', back_populates='transactions', lazy='select')

    def to_dict(self):
        return {
            'id': self.id,
            'wallet_id': self.wallet_id,
            'amount': float(self.amount) if self.amount is not None else 0.00,
            'transaction_type': self.transaction_type,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<WalletTransaction {self.id}: {self.transaction_type} {self.amount}>"


class WithdrawalRequest(db.Model):
    """نموذج طلبات سحب الأرباح"""
    __tablename__ = 'withdrawal_requests'

    __table_args__ = (
        db.Index('idx_withdrawal_wallet_id', 'wallet_id'),
        db.Index('idx_withdrawal_status', 'status'),
        db.Index('idx_withdrawal_created', 'created_at'),
        {'extend_existing': True}
    )

    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('supplier_wallets.id', ondelete='CASCADE'), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    status = db.Column(db.String(50), default='pending', nullable=False)  # pending, approved, rejected
    notes = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    wallet = db.relationship('SupplierWallet', back_populates='withdrawal_requests', lazy='select')

    def to_dict(self):
        return {
            'id': self.id,
            'wallet_id': self.wallet_id,
            'amount': float(self.amount) if self.amount is not None else 0.00,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f"<WithdrawalRequest {self.id}: {self.amount} - {self.status}>"
