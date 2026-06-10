# coding: utf-8
# 📂 apps/models/wallet_db.py - نظام المحافظ والعمليات المالية (مُحصن)

from apps.extensions import db
from datetime import datetime
from sqlalchemy import CheckConstraint

class SupplierWallet(db.Model):
    __tablename__ = 'supplier_wallets'
    
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False, unique=True)
    
    # 🔗 جسر الربط: يتيح الوصول لبيانات المورد من المحفظة مباشرة
    supplier = db.relationship('Supplier', backref=db.backref('wallet', uselist=False))
    
    # استخدام Numeric للدقة المالية (15 رقم، 2 للكسور)
    balance_sar = db.Column(db.Numeric(15, 2), default=0.0)
    balance_yer = db.Column(db.Numeric(15, 2), default=0.0)
    balance_usd = db.Column(db.Numeric(15, 2), default=0.0)
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 🛡️ قيود قاعدة البيانات (تمنع تخزين أرصدة سالبة على مستوى الجدول)
    __table_args__ = (
        CheckConstraint('balance_sar >= 0', name='check_sar_positive'),
        CheckConstraint('balance_yer >= 0', name='check_yer_positive'),
        CheckConstraint('balance_usd >= 0', name='check_usd_positive'),
    )

    # 🔗 جسر الربط بالمعاملات: يتيح الوصول لجميع عمليات المحفظة
    transactions = db.relationship('WalletTransaction', backref='wallet', lazy='dynamic')

class WalletTransaction(db.Model):
    __tablename__ = 'wallet_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('supplier_wallets.id'), nullable=False)
    
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False) # 'SAR', 'YER', 'USD'
    transaction_type = db.Column(db.String(20), nullable=False) # 'credit', 'debit'
    description = db.Column(db.String(255))
    
    # توثيق زمني للعملية
    status = db.Column(db.String(20), default='completed') 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 🛡️ الحماية: منع العمليات المالية غير المنطقية
    __table_args__ = (
        CheckConstraint('amount > 0', name='check_amount_positive'),
    )
