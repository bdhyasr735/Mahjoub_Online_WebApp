# -*- coding: utf-8 -*-
# 📂 apps/models/wallet_db.py

import os
import base64
import secrets
import string
from datetime import datetime, timedelta
from decimal import Decimal
from cryptography.fernet import Fernet
from sqlalchemy import event, select, update
from apps.extensions import db


class SupplierWallet(db.Model):
    """محفظة الموردين: الأرصدة والبيانات المشفرة بأعلى معايير الأمان (ريال سعودي SAR فقط)."""
    __tablename__ = 'supplier_wallets'

    __table_args__ = (
        db.Index('idx_wall_lookup', 'supplier_id', 'wallet_code'),
        db.Index('idx_wall_activity', 'updated_at'),
        {'extend_existing': True}
    )

    id = db.Column(db.Integer, primary_key=True)
    wallet_code = db.Column(db.String(50), unique=True, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False, unique=True)
    
    status = db.Column(db.String(20), default='active', nullable=False)

    balance_sar = db.Column(db.Numeric(18, 2), default=0.00, nullable=False)
    balance_pending = db.Column(db.Numeric(18, 2), default=0.00)
    total_withdrawn = db.Column(db.Numeric(18, 2), default=0.00)

    _bank_details_enc = db.Column(db.String(500), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    supplier = db.relationship('Supplier', back_populates='wallet', lazy='joined')
    transactions = db.relationship('WalletTransaction', back_populates='wallet', cascade="all, delete-orphan", lazy='selectin')

    @staticmethod
    def _get_fernet():
        key = os.environ.get('ENCRYPTION_KEY', 'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8V=')
        try:
            return Fernet(key.encode('utf-8'))
        except Exception:
            b64_key = base64.urlsafe_b64encode(key.encode('utf-8')[:32].ljust(32, b'0'))
            return Fernet(b64_key)

    @property
    def bank_details(self):
        if not self._bank_details_enc:
            return None
        try:
            return self._get_fernet().decrypt(self._bank_details_enc.encode('utf-8')).decode('utf-8')
        except Exception:
            return None

    @bank_details.setter
    def bank_details(self, value):
        if value:
            self._bank_details_enc = self._get_fernet().encrypt(str(value).encode('utf-8')).decode('utf-8')
        else:
            self._bank_details_enc = None

    @property
    def formatted_time(self):
        if self.updated_at:
            local_time = self.updated_at + timedelta(hours=3)
            return local_time.strftime('%Y-%m-%d | %I:%M:%S %p')
        return "-"

    def to_dict(self):
        return {
            'id': self.id,
            'wallet_code': self.wallet_code,
            'status': self.status,
            'supplier_id': self.supplier_id,
            'balance_sar': float(self.balance_sar or 0.0),
            'bank_details': self.bank_details,
            'formatted_time': self.formatted_time,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class WalletTransaction(db.Model):
    """سجل الحركات المالية الموحد بالريال السعودي مع التوثيق المالي المشفر."""
    __tablename__ = 'wallet_transactions'

    __table_args__ = (
        db.Index('idx_trans_wallet_history', 'wallet_id', 'created_at'),
        db.Index('idx_trans_lookup', 'voucher_number', 'reference_number'),
        db.Index('idx_trans_status_type', 'status', 'trans_type'),
        {'extend_existing': True}
    )

    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('supplier_wallets.id'), nullable=False)
    
    trans_type = db.Column(db.String(30), nullable=False)
    status = db.Column(db.String(30), default='completed') 
    amount = db.Column(db.Numeric(18, 2), nullable=False)
    currency = db.Column(db.String(5), nullable=False, default='SAR')
    balance_before = db.Column(db.Numeric(18, 2), nullable=False)
    balance_after = db.Column(db.Numeric(18, 2), nullable=False)
    
    # [بيانات التوثيق المالي]
    transfer_number = db.Column(db.String(100), nullable=True)
    approval_ref = db.Column(db.String(100), nullable=True)
    payout_bank = db.Column(db.String(100), nullable=True)
    
    _description_enc = db.Column(db.String(500), nullable=True)
    
    reference_number = db.Column(db.String(80), unique=True, nullable=True)
    voucher_number = db.Column(db.String(50), unique=True, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    wallet = db.relationship('SupplierWallet', back_populates='transactions', lazy='joined')

    @property
    def description(self):
        if not self._description_enc:
            return None
        try:
            key = os.environ.get('ENCRYPTION_KEY', 'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8V=')
            return Fernet(key.encode('utf-8')).decrypt(self._description_enc.encode('utf-8')).decode('utf-8')
        except Exception:
            return None

    @description.setter
    def description(self, value):
        if value:
            key = os.environ.get('ENCRYPTION_KEY', 'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8V=')
            self._description_enc = Fernet(key.encode('utf-8')).encrypt(str(value).encode('utf-8')).decode('utf-8')
        else:
            self._description_enc = None

    @property
    def formatted_time(self):
        if self.created_at:
            local_time = self.created_at + timedelta(hours=3)
            return local_time.strftime('%Y-%m-%d | %I:%M:%S %p')
        return "-"

    def to_dict(self):
        return {
            'id': self.id,
            'trans_type': self.trans_type,
            'status': self.status,
            'amount': float(self.amount or 0.0),
            'currency': self.currency,
            'reference_number': self.reference_number,
            'voucher_number': self.voucher_number,
            'transfer_number': self.transfer_number,
            'approval_ref': self.approval_ref,
            'payout_bank': self.payout_bank,
            'description': self.description,
            'formatted_time': self.formatted_time,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


def generate_unique_voucher_number(connection, length=6, prefix="VCH-"):
    characters = string.ascii_uppercase + string.digits
    while True:
        random_str = ''.join(secrets.choice(characters) for _ in range(length))
        candidate_voucher = f"{prefix}{random_str}"
        existing = connection.execute(
            select(WalletTransaction.voucher_number)
            .where(WalletTransaction.voucher_number == candidate_voucher)
        ).scalar()
        if not existing:
            return candidate_voucher


@event.listens_for(WalletTransaction, 'before_insert')
def process_wallet_transaction_before_insert(mapper, connection, target):
    wallet_table = SupplierWallet.__table__
    wallet_row = connection.execute(
        select(wallet_table).where(wallet_table.c.id == target.wallet_id)
    ).mappings().first()

    sup_code = f"SUPP{target.wallet_id}"
    
    if wallet_row:
        supplier_id = wallet_row.get('supplier_id')
        supplier_table = db.metadata.tables.get('suppliers')
        if supplier_table is not None:
            sup_code_val = connection.execute(
                select(supplier_table.c.supplier_code).where(supplier_table.c.id == supplier_id)
            ).scalar()
            if sup_code_val:
                sup_code = sup_code_val

    if not target.reference_number:
        characters = string.ascii_uppercase + string.digits
        while True:
            random_6_code = ''.join(secrets.choice(characters) for _ in range(6))
            candidate_ref = f"TRX-{sup_code}-{random_6_code}"
            existing_ref = connection.execute(
                select(WalletTransaction.reference_number)
                .where(WalletTransaction.reference_number == candidate_ref)
            ).scalar()
            if not existing_ref:
                target.reference_number = candidate_ref
                break

    if not target.voucher_number:
        target.voucher_number = generate_unique_voucher_number(connection, length=6, prefix="VCH-")

    if wallet_row:
        # الاعتماد الثابت على balance_sar فقط
        current_bal = Decimal(str(wallet_row.get('balance_sar', 0)))
        
        target.balance_before = current_bal
        is_credit = target.trans_type in ['credit', 'sale_revenue', 'deposit', 'refund', 'adjustment_credit']
        target.balance_after = (current_bal + Decimal(str(target.amount))) if is_credit else (current_bal - Decimal(str(target.amount)))

        connection.execute(
            update(wallet_table)
            .where(wallet_table.c.id == target.wallet_id)
            .values({'balance_sar': target.balance_after, 'updated_at': datetime.utcnow()})
        )


class WithdrawalRequest(db.Model):
    """جدول طلبات سحب الأرباح للموردين بالريال السعودي."""
    __tablename__ = 'withdrawal_requests'

    __table_args__ = (
        db.Index('idx_withdrawal_supplier', 'supplier_id', 'status'),
        {'extend_existing': True}
    )

    id = db.Column(db.Integer, primary_key=True)
    request_number = db.Column(db.String(50), unique=True, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    wallet_id = db.Column(db.Integer, db.ForeignKey('supplier_wallets.id'), nullable=False)
    
    amount = db.Column(db.Numeric(18, 2), nullable=False)
    currency = db.Column(db.String(5), nullable=False, default='SAR')
    
    payout_method = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(30), default='pending', nullable=False)
    notes = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    wallet = db.relationship('SupplierWallet', backref=db.backref('withdrawal_requests', lazy='selectin'))

    def to_dict(self):
        return {
            'id': self.id,
            'request_number': self.request_number,
            'amount': float(self.amount or 0.0),
            'currency': self.currency,
            'payout_method': self.payout_method,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
