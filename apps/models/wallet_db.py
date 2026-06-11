# coding: utf-8
# 📂 apps/models/wallet_db.py - نظام المحافظ (مُشفر بالكامل بـ AES-256)

import os
from apps.extensions import db
from datetime import datetime
from cryptography.fernet import Fernet
from flask import current_app

# دالة مساعدة للحصول على أداة التشفير
def get_cipher():
    key = current_app.config.get('ENCRYPTION_KEY')
    return Fernet(key.encode())

class SupplierWallet(db.Model):
    __tablename__ = 'supplier_wallets'
    
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False, unique=True)
    supplier = db.relationship('Supplier', back_populates='wallet')
    
    # حقول مشفرة (تخزن كـ String)
    _balance_sar = db.Column(db.String(255), default="0.0")
    _balance_yer = db.Column(db.String(255), default="0.0")
    _balance_usd = db.Column(db.String(255), default="0.0")
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # خصائص فك وتشفير تلقائي
    @property
    def balance_sar(self): return float(get_cipher().decrypt(self._balance_sar.encode()).decode())
    @balance_sar.setter
    def balance_sar(self, value): self._balance_sar = get_cipher().encrypt(str(value).encode()).decode()

    @property
    def balance_yer(self): return float(get_cipher().decrypt(self._balance_yer.encode()).decode())
    @balance_yer.setter
    def balance_yer(self, value): self._balance_yer = get_cipher().encrypt(str(value).encode()).decode()

    @property
    def balance_usd(self): return float(get_cipher().decrypt(self._balance_usd.encode()).decode())
    @balance_usd.setter
    def balance_usd(self, value): self._balance_usd = get_cipher().encrypt(str(value).encode()).decode()

    transactions = db.relationship('WalletTransaction', back_populates='wallet', lazy='dynamic')

    def add_transaction(self, amount, currency, transaction_type, description=None):
        transaction = WalletTransaction(
            wallet_id=self.id,
            amount=amount,
            currency=currency.upper(),
            transaction_type=transaction_type,
            description=description
        )
        
        multiplier = 1 if transaction_type == 'credit' else -1
        
        if currency.upper() == 'SAR': self.balance_sar += (amount * multiplier)
        elif currency.upper() == 'YER': self.balance_yer += (amount * multiplier)
        elif currency.upper() == 'USD': self.balance_usd += (amount * multiplier)
            
        db.session.add(transaction)
        db.session.commit()
        return transaction

class WalletTransaction(db.Model):
    __tablename__ = 'wallet_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('supplier_wallets.id'), nullable=False)
    wallet = db.relationship('SupplierWallet', back_populates='transactions')
    
    # حقل مشفر
    _amount = db.Column(db.String(255), nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(255))
    status = db.Column(db.String(20), default='completed') 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def amount(self): return float(get_cipher().decrypt(self._amount.encode()).decode())
    @amount.setter
    def amount(self, value): self._amount = get_cipher().encrypt(str(value).encode()).decode()
