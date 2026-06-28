# coding: utf-8
# 📂 apps/models/wallet_db.py

import os
from datetime import datetime
from cryptography.fernet import Fernet
from apps.extensions import db

class SupplierWallet(db.Model):
    """موديل محفظة الموردين: الأرصدة والبيانات المشفرة."""
    __tablename__ = 'supplier_wallets'

    __table_args__ = (
        db.Index('idx_wall_code', 'wallet_code'),
        db.Index('idx_wall_supplier_id', 'supplier_id'),
        db.Index('idx_wall_updated', 'updated_at'),
        {'extend_existing': True}
    )
    
    id = db.Column(db.Integer, primary_key=True)
    wallet_code = db.Column(db.String(50), unique=True, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False, unique=True)
    
    # الأرصدة المالية - باستخدام Numeric للدقة المحاسبية
    balance_yer = db.Column(db.Numeric(18, 2), default=0.00) 
    balance_usd = db.Column(db.Numeric(18, 2), default=0.00) 
    balance_sar = db.Column(db.Numeric(18, 2), default=0.00) 
    balance_pending = db.Column(db.Numeric(18, 2), default=0.00)    
    total_withdrawn = db.Column(db.Numeric(18, 2), default=0.00)    
    
    _bank_details_enc = db.Column(db.String(500), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    supplier = db.relationship('apps.models.supplier_db.Supplier', back_populates='wallet')
    transactions = db.relationship('WalletTransaction', back_populates='wallet', cascade="all, delete-orphan")

    # --- نظام التشفير (AES) ---
    @staticmethod
    def _get_key():
        key = os.environ.get('ENCRYPTION_KEY')
        return key.encode() if key else b'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8Vq='

    @property
    def bank_details(self):
        if not self._bank_details_enc: return None
        try:
            f = Fernet(self._get_key())
            return f.decrypt(self._bank_details_enc.encode()).decode()
        except: return None

    @bank_details.setter
    def bank_details(self, value):
        if value:
            f = Fernet(self._get_key())
            self._bank_details_enc = f.encrypt(str(value).encode()).decode()
        else: self._bank_details_enc = None

class WalletTransaction(db.Model):
    """سجل الحركات المالية (دفتر الأستاذ) لكل محفظة."""
    __tablename__ = 'wallet_transactions'
    
    __table_args__ = (
        db.Index('idx_trans_wallet', 'wallet_id'),
        db.Index('idx_trans_date', 'created_at'),
        db.Index('idx_trans_source', 'source_type'), # فهرس لتحسين البحث عن نوع الحركة
        {'extend_existing': True}
    )

    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('supplier_wallets.id'), nullable=False)
    
    # تفاصيل الحركة
    trans_type = db.Column(db.String(20), nullable=False) # 'credit', 'debit'
    source_type = db.Column(db.String(20), default='manual') # 'order', 'voucher', 'manual'
    amount = db.Column(db.Numeric(18, 2), nullable=False)
    currency = db.Column(db.String(5), nullable=False) # 'SAR', 'YER', 'USD'
    
    # تفاصيل السند
    description = db.Column(db.String(255))
    reference_number = db.Column(db.String(50)) # رقم سند التسوية أو رقم الطلب
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    wallet = db.relationship('SupplierWallet', back_populates='transactions')
