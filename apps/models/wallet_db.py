# coding: utf-8
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
    """محفظة الموردين: الأرصدة والبيانات المشفرة بأعلى معايير الأمان."""
    __tablename__ = 'supplier_wallets'

    __table_args__ = (
        db.Index('idx_wall_lookup', 'supplier_id', 'wallet_code'),
        db.Index('idx_wall_activity', 'updated_at'),
        {'extend_existing': True}
    )

    id = db.Column(db.Integer, primary_key=True)
    wallet_code = db.Column(db.String(50), unique=True, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False, unique=True)
    
    # تم إضافة الحالة هنا لمنع أخطاء الاستعلام
    status = db.Column(db.String(20), default='active', nullable=False)

    balance_yer = db.Column(db.Numeric(18, 2), default=0.00)
    balance_usd = db.Column(db.Numeric(18, 2), default=0.00)
    balance_sar = db.Column(db.Numeric(18, 2), default=0.00)
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
            'formatted_time': self.formatted_time
        }


class WalletTransaction(db.Model):
    """سجل الحركات المالية الموحد مع تشفير حقل الوصف والفهرسة الفائقة."""
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
    
    _description_enc = db.Column(db.String(500), nullable=True)
    reference_number = db.Column(db.String(80), unique=True, nullable=True)
    voucher_number = db.Column(db.String(50), unique=True, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    wallet = db.relationship('SupplierWallet', back_populates='transactions', lazy='joined')

    @property
    def description(self):
        if not self._description_enc: return None
        try:
            key = os.environ.get('ENCRYPTION_KEY', 'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8V=')
            return Fernet(key.encode('utf-8')).decrypt(self._description_enc.encode('utf-8')).decode('utf-8')
        except: return None

    @description.setter
    def description(self, value):
        if value:
            key = os.environ.get('ENCRYPTION_KEY', 'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8V=')
            self._description_enc = Fernet(key.encode('utf-8')).encrypt(str(value).encode('utf-8')).decode('utf-8')
        else: self._description_enc = None

    def to_dict(self):
        return {
            'id': self.id,
            'trans_type': self.trans_type,
            'status': self.status,
            'amount': float(self.amount or 0.0),
            'description': self.description,
            'created_at': self.created_at.isoformat()
        }

def generate_unique_voucher_number(connection, length=6, prefix="VCH-"):
    characters = string.ascii_uppercase + string.digits
    while True:
        candidate = f"{prefix}{''.join(secrets.choice(characters) for _ in range(length))}"
        if not connection.execute(select(WalletTransaction.id).where(WalletTransaction.voucher_number == candidate)).scalar():
            return candidate

@event.listens_for(WalletTransaction, 'before_insert')
def process_wallet_transaction_before_insert(mapper, connection, target):
    wallet_table = SupplierWallet.__table__
    wallet_row = connection.execute(select(wallet_table).where(wallet_table.c.id == target.wallet_id)).mappings().first()
    
    if not target.reference_number:
        chars = string.ascii_uppercase + string.digits
        while True:
            candidate = f"TRX-SUPP{target.wallet_id}-{''.join(secrets.choice(chars) for _ in range(6))}"
            if not connection.execute(select(WalletTransaction.id).where(WalletTransaction.reference_number == candidate)).scalar():
                target.reference_number = candidate
                break
    
    if not target.voucher_number:
        target.voucher_number = generate_unique_voucher_number(connection)

    if wallet_row:
        attr = f'balance_{(target.currency or "sar").lower()}'
        current_bal = Decimal(str(wallet_row.get(attr, 0)))
        target.balance_before = current_bal
        is_credit = target.trans_type in ['credit', 'sale_revenue', 'deposit', 'refund']
        target.balance_after = (current_bal + Decimal(str(target.amount))) if is_credit else (current_bal - Decimal(str(target.amount)))
        connection.execute(update(wallet_table).where(wallet_table.c.id == target.wallet_id).values({attr: target.balance_after, 'updated_at': datetime.utcnow()}))
