# coding: utf-8
# 📂 apps/models/wallet_db.py - نظام المحافظ والعمليات المالية (مُحصن)

from apps.extensions import db
from datetime import datetime
from sqlalchemy import CheckConstraint

class SupplierWallet(db.Model):
    __tablename__ = 'supplier_wallets'
    
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False, unique=True)
    
    # 🔗 الربط الصريح
    supplier = db.relationship('Supplier', back_populates='wallet')
    
    # استخدام Numeric للدقة المالية
    balance_sar = db.Column(db.Numeric(15, 2), default=0.0)
    balance_yer = db.Column(db.Numeric(15, 2), default=0.0)
    balance_usd = db.Column(db.Numeric(15, 2), default=0.0)
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 🛡️ قيود قاعدة البيانات
    __table_args__ = (
        CheckConstraint('balance_sar >= 0', name='check_sar_positive'),
        CheckConstraint('balance_yer >= 0', name='check_yer_positive'),
        CheckConstraint('balance_usd >= 0', name='check_usd_positive'),
    )

    # 🔗 الربط بالمعاملات
    transactions = db.relationship('WalletTransaction', back_populates='wallet', lazy='dynamic')

    def add_transaction(self, amount, currency, transaction_type, description=None):
        """دالة مركزية لإضافة معاملة وتحديث الرصيد تلقائياً"""
        # 1. إنشاء سجل المعاملة
        transaction = WalletTransaction(
            wallet_id=self.id,
            amount=amount,
            currency=currency.upper(),
            transaction_type=transaction_type,
            description=description
        )
        
        # 2. تحديث الرصيد بناءً على العملة ونوع العملية
        multiplier = 1 if transaction_type == 'credit' else -1
        
        if currency.upper() == 'SAR':
            self.balance_sar += (amount * multiplier)
        elif currency.upper() == 'YER':
            self.balance_yer += (amount * multiplier)
        elif currency.upper() == 'USD':
            self.balance_usd += (amount * multiplier)
            
        db.session.add(transaction)
        db.session.commit()
        return transaction

class WalletTransaction(db.Model):
    __tablename__ = 'wallet_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('supplier_wallets.id'), nullable=False)
    
    # 🔗 ربط المعاملة بالمحفظة
    wallet = db.relationship('SupplierWallet', back_populates='transactions')
    
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False) # 'SAR', 'YER', 'USD'
    transaction_type = db.Column(db.String(20), nullable=False) # 'credit', 'debit'
    description = db.Column(db.String(255))
    
    status = db.Column(db.String(20), default='completed') 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint('amount > 0', name='check_amount_positive'),
    )
