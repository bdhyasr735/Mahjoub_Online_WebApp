# coding: utf-8
# 📂 apps/models/treasury_db.py

import os
from datetime import datetime
from cryptography.fernet import Fernet
from apps.extensions import db

class PlatformTreasury(db.Model):
    """جدول أرصدة الخزينة المركزية للمنصة."""
    __tablename__ = 'platform_treasury'
    
    id = db.Column(db.Integer, primary_key=True)
    treasury_name = db.Column(db.String(100), default="الخزينة الرئيسية")
    
    # الأرصدة (بدون تشفير للعمليات الحسابية السريعة)
    balance_yer = db.Column(db.Numeric(18, 2), default=0.00)
    balance_usd = db.Column(db.Numeric(18, 2), default=0.00)
    balance_sar = db.Column(db.Numeric(18, 2), default=0.00)
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class WithdrawalRequest(db.Model):
    """جدول طلبات سحب الموردين من محافظهم إلى الخزينة."""
    __tablename__ = 'withdrawal_requests'

    __table_args__ = (
        db.Index('idx_wd_supplier', 'supplier_id'),
        db.Index('idx_wd_status', 'status'),
        db.Index('idx_wd_created', 'created_at'),
        {'extend_existing': True}
    )

    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    
    amount = db.Column(db.Numeric(18, 2), nullable=False)
    currency = db.Column(db.String(5), nullable=False)
    status = db.Column(db.String(20), default='pending') # pending, approved, rejected
    
    # [تشفير حساس]: معلومات التحويل البنكي أو وسيلة السحب
    _details_enc = db.Column(db.String(500), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)
    
    # العلاقات
    supplier = db.relationship('Supplier', backref='withdrawal_requests')

    # --- نظام التشفير (AES) ---
    @staticmethod
    def _get_key():
        key = os.environ.get('ENCRYPTION_KEY', 'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8Vq=')
        return key.encode()

    @property
    def details(self):
        if not self._details_enc: return None
        try:
            return Fernet(self._get_key()).decrypt(self._details_enc.encode()).decode()
        except: return None

    @details.setter
    def details(self, value):
        if value:
            self._details_enc = Fernet(self._get_key()).encrypt(str(value).encode()).decode()

    def __repr__(self):
        return f'<WithdrawalRequest {self.id} | Status: {self.status}>'
