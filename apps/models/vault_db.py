# coding: utf-8
# 📂 apps/models/vault_db.py - الخزنة المركزية (مشفرة بـ AES-256)

import os
from apps.extensions import db
from datetime import datetime
from sqlalchemy import CheckConstraint
from cryptography.fernet import Fernet
import hashlib

# إعداد مفتاح التشفير
KEY = os.environ.get('ENCRYPTION_KEY', 'put-your-32-byte-key-here-or-generate-it').encode()
cipher = Fernet(KEY)

class AdminVault(db.Model):
    __tablename__ = 'admin_vault'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), default="الخزنة المركزية")
    
    # حقول مشفرة (تخزن كـ String)
    _balance_sar = db.Column(db.String(255), default="0.0")
    _balance_yer = db.Column(db.String(255), default="0.0")
    _balance_usd = db.Column(db.String(255), default="0.0")
    
    integrity_hash = db.Column(db.String(64), nullable=True)

    @property
    def balance_sar(self):
        return float(cipher.decrypt(self._balance_sar.encode()).decode())

    @balance_sar.setter
    def balance_sar(self, value):
        self._balance_sar = cipher.encrypt(str(value).encode()).decode()

    @property
    def balance_yer(self):
        return float(cipher.decrypt(self._balance_yer.encode()).decode())

    @balance_yer.setter
    def balance_yer(self, value):
        self._balance_yer = cipher.encrypt(str(value).encode()).decode()

    @property
    def balance_usd(self):
        return float(cipher.decrypt(self._balance_usd.encode()).decode())

    @balance_usd.setter
    def balance_usd(self, value):
        self._balance_usd = cipher.encrypt(str(value).encode()).decode()

    def generate_integrity_hash(self):
        data = f"{self.balance_sar}{self.balance_yer}{self.balance_usd}"
        return hashlib.sha256(data.encode()).hexdigest()

    def update_balance(self, sar_delta=0, yer_delta=0, usd_delta=0):
        self.balance_sar = self.balance_sar + sar_delta
        self.balance_yer = self.balance_yer + yer_delta
        self.balance_usd = self.balance_usd + usd_delta
        self.integrity_hash = self.generate_integrity_hash()

class VaultTransaction(db.Model):
    __tablename__ = 'vault_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # تشفير المبلغ المالي في العمليات
    _amount = db.Column(db.String(255), nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin_user.id'), nullable=True)
    reference_id = db.Column(db.String(100), nullable=True)

    @property
    def amount(self):
        return float(cipher.decrypt(self._amount.encode()).decode())

    @amount.setter
    def amount(self, value):
        self._amount = cipher.encrypt(str(value).encode()).decode()

    def __repr__(self):
        return f'<VaultTransaction {self.transaction_type} {self.amount} {self.currency}>'
