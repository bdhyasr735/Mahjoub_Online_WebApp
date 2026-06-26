# coding: utf-8
# 📂 apps/models/wallet_db.py

import os
from datetime import datetime
from cryptography.fernet import Fernet
from apps.extensions import db

class SupplierWallet(db.Model):
    __tablename__ = 'supplier_wallets'

    # [صمام الأمان]: فهرسة مسمّاة ومنع تكرار التعريف لضمان عدم انهيار السيرفر
    __table_args__ = (
        db.Index('idx_wall_code', 'wallet_code'),
        db.Index('idx_wall_supplier_id', 'supplier_id'),
        db.Index('idx_wall_updated', 'updated_at'),
        {'extend_existing': True}
    )
    
    id = db.Column(db.Integer, primary_key=True)
    wallet_code = db.Column(db.String(50), unique=True, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False, unique=True)
    
    # [دقة مالية]: استخدام Numeric (18,2) للحسابات الحساسة
    balance_yer = db.Column(db.Numeric(18, 2), default=0.00) 
    balance_usd = db.Column(db.Numeric(18, 2), default=0.00) 
    balance_sar = db.Column(db.Numeric(18, 2), default=0.00) 
    balance_pending = db.Column(db.Numeric(18, 2), default=0.00)    
    total_withdrawn = db.Column(db.Numeric(18, 2), default=0.00)    
    
    # [تشفير AES]: للبيانات الحساسة
    _bank_details_enc = db.Column(db.String(500), nullable=True)
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # [المسار الكامل]: الربط السيادي لمنع خطأ Multiple classes found
    supplier = db.relationship(
        'apps.models.supplier_db.Supplier', 
        back_populates='wallet'
    )

    # --- نظام التشفير (AES) ---
    @staticmethod
    def _get_key():
        return os.environ.get('ENCRYPTION_KEY', 'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8Vq=').encode()

    @property
    def bank_details(self):
        if not self._bank_details_enc: return None
        try:
            return Fernet(self._get_key()).decrypt(self._bank_details_enc.encode()).decode()
        except: return None

    @bank_details.setter
    def bank_details(self, value):
        if value:
            self._bank_details_enc = Fernet(self._get_key()).encrypt(str(value).encode()).decode()

    def __repr__(self):
        return f'<SupplierWallet {self.wallet_code} | YER: {self.balance_yer}>'
