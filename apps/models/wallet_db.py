# coding: utf-8
# 📂 apps/models/wallet_db.py - نظام المحافظ والحركات السيادي (مُشفر ومفهرس للتحمل العالي)

from apps.extensions import db
from apps.utils.security import AESCipher
from datetime import datetime

class SupplierWallet(db.Model):
    __tablename__ = 'supplier_wallets'
    
    id = db.Column(db.Integer, primary_key=True)
    # ⚡ فهرسة supplier_id للوصول السريع لمحفظة المورد
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    
    supplier = db.relationship('Supplier', back_populates='wallet', overlaps="supplier_owner")
    
    # حقول مشفرة (لا تفهرس لأن التشفير يغير القيم)
    _balance_sar = db.Column(db.String(255), default=AESCipher.encrypt("0.0"))
    _balance_yer = db.Column(db.String(255), default=AESCipher.encrypt("0.0"))
    _balance_usd = db.Column(db.String(255), default=AESCipher.encrypt("0.0"))
    
    _frozen_sar = db.Column(db.String(255), default=AESCipher.encrypt("0.0"))
    _frozen_yer = db.Column(db.String(255), default=AESCipher.encrypt("0.0"))
    _frozen_usd = db.Column(db.String(255), default=AESCipher.encrypt("0.0"))
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    
    transactions = db.relationship('WalletTransaction', back_populates='wallet', lazy='dynamic', cascade="all, delete-orphan")

    # [Properties...] (نفس كودك السابق لفك التشفير يعمل ببراعة)
    # ملاحظة: حافظت على منطق Properties الذي كتبته لأنه الأصح للأمان.

class WalletTransaction(db.Model):
    __tablename__ = 'wallet_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    # ⚡ فهرسة wallet_id لجلب معاملات محفظة معينة بسرعة البرق
    wallet_id = db.Column(db.Integer, db.ForeignKey('supplier_wallets.id', ondelete='CASCADE'), nullable=False, index=True)
    wallet = db.relationship('SupplierWallet', back_populates='transactions')
    
    # ⚡ فهرسة order_id للبحث السريع عن حالة طلب معين
    order_id = db.Column(db.String(100), nullable=True, index=True)
    
    _amount = db.Column(db.String(255), nullable=False)
    
    # ⚡ فهرسة للعملة والنوع والتاريخ للتقارير المالية والفلترة
    currency = db.Column(db.String(3), nullable=False, index=True)
    transaction_type = db.Column(db.String(30), nullable=False, index=True)
    status = db.Column(db.String(20), default='completed', index=True) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    @property
    def amount(self): 
        val = AESCipher.decrypt(self._amount)
        return float(val) if val else 0.0
    
    @amount.setter
    def amount(self, value): 
        self._amount = AESCipher.encrypt(str(value))
