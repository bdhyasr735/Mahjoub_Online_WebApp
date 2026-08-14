# coding: utf-8
# 📂 apps/models/wallet_db.py

import os
import base64
import secrets
import string
from datetime import datetime
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
        key = os.environ.get('ENCRYPTION_KEY')
        if not key:
            key = 'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8V='
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

    def to_dict(self):
        return {
            'id': self.id,
            'wallet_code': self.wallet_code,
            'supplier_id': self.supplier_id,
            'balance_yer': float(self.balance_yer or 0.0),
            'balance_usd': float(self.balance_usd or 0.0),
            'balance_sar': float(self.balance_sar or 0.0),
            'bank_details': self.bank_details,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
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
    owner_type = db.Column(db.String(20), default='supplier')
    owner_id = db.Column(db.Integer, nullable=False)

    trans_type = db.Column(db.String(30), nullable=False)
    status = db.Column(db.String(30), default='completed') 
    amount = db.Column(db.Numeric(18, 2), nullable=False)
    currency = db.Column(db.String(5), nullable=False, default='SAR')
    balance_before = db.Column(db.Numeric(18, 2), nullable=False)
    balance_after = db.Column(db.Numeric(18, 2), nullable=False)
    
    # [التشفير السيادي]: وصف الحركة مشفر بالكامل
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

    def to_dict(self):
        return {
            'id': self.id,
            'trans_type': self.trans_type,
            'status': self.status,
            'amount': float(self.amount or 0.0),
            'reference_number': self.reference_number,
            'voucher_number': self.voucher_number,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


def generate_unique_voucher_number(connection, length=6, prefix="VCH-"):
    """توليد رقم سند فريد يتكون من 6 خانات عشوائية (أرقام وحروف مخلوطة) مع الفحص المباشر لعدم التكرار."""
    characters = string.ascii_uppercase + string.digits  # حروف كبيرة وأرقام (A-Z, 0-9)
    
    while True:
        random_str = ''.join(secrets.choice(characters) for _ in range(length))
        candidate_voucher = f"{prefix}{random_str}"
        
        # التأكد الفوري من قاعدة البيانات لعدم تكرار الرقم نهائياً
        existing = connection.execute(
            select(WalletTransaction.voucher_number)
            .where(WalletTransaction.voucher_number == candidate_voucher)
        ).scalar()
        
        if not existing:
            return candidate_voucher


# --- مشغل الأحداث (Engine) للتسوية التلقائية ---
@event.listens_for(WalletTransaction, 'before_insert')
def process_wallet_transaction_before_insert(mapper, connection, target):
    """توليد الأرقام المرجعية وأرقام السندات المكونة من 6 خانات عشوائية وحساب الأرصدة لحظياً."""
    
    wallet_table = SupplierWallet.__table__
    
    # 1. جلب بيانات المحفظة لمعرفة supplier_id
    wallet_row = connection.execute(
        select(wallet_table).where(wallet_table.c.id == target.wallet_id)
    ).mappings().first()

    sup_code = f"SUPP{target.wallet_id}"  # قيمة افتراضية احتياطية
    
    if wallet_row:
        supplier_id = wallet_row.get('supplier_id')
        # 2. جلب كود المورد (supplier_code) من جدول suppliers مباشرة
        supplier_table = db.metadata.tables.get('suppliers')
        if supplier_table is not None:
            sup_code_val = connection.execute(
                select(supplier_table.c.supplier_code).where(supplier_table.c.id == supplier_id)
            ).scalar()
            if sup_code_val:
                sup_code = sup_code_val

    # 3. إنشاء رقم المرجع المخصص بحيث يحتوي على 6 خانات عشوائية مخلوطة بالأحرف والأرقام
    if not target.reference_number:
        characters = string.ascii_uppercase + string.digits
        
        while True:
            random_6_code = ''.join(secrets.choice(characters) for _ in range(6))
            candidate_ref = f"TRX-{sup_code}-{random_6_code}"
            
            # التحقق المباشر من قاعدة البيانات لضمان عدم التكرار نهائياً
            existing_ref = connection.execute(
                select(WalletTransaction.reference_number)
                .where(WalletTransaction.reference_number == candidate_ref)
            ).scalar()
            
            if not existing_ref:
                target.reference_number = candidate_ref
                break

    # 4. توليد رقم السند العشوائي الفريد (6 خانات حروف وأرقام) تلقائياً
    if not target.voucher_number:
        target.voucher_number = generate_unique_voucher_number(connection, length=6, prefix="VCH-")

    # 5. حساب الأرصدة (Balance Logic)
    if wallet_row:
        attr = f'balance_{(target.currency or "sar").lower()}'
        current_bal = Decimal(str(wallet_row.get(attr, 0)))
        
        target.balance_before = current_bal
        is_credit = target.trans_type in ['credit', 'sale_revenue', 'deposit', 'refund', 'adjustment_credit']
        target.balance_after = (current_bal + Decimal(str(target.amount))) if is_credit else (current_bal - Decimal(str(target.amount)))

        # تحديث المحفظة مباشرة
        connection.execute(
            update(wallet_table)
            .where(wallet_table.c.id == target.wallet_id)
            .values({attr: target.balance_after, 'updated_at': datetime.utcnow()})
        )