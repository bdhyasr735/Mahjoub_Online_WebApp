# coding: utf-8
# 📂 apps/models/vault_db.py - الخزنة المركزية (مُحصنة بـ AES-256 ومفهرسة للتدقيق المالي)

from apps.extensions import db
from datetime import datetime
from apps.utils.security import AESCipher
import hashlib

class AdminVault(db.Model):
    __tablename__ = 'admin_vault'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), default="الخزنة المركزية")
    
    # حقول مشفرة
    _balance_sar = db.Column(db.String(255), default=lambda: AESCipher.encrypt("0.0"))
    _balance_yer = db.Column(db.String(255), default=lambda: AESCipher.encrypt("0.0"))
    _balance_usd = db.Column(db.String(255), default=lambda: AESCipher.encrypt("0.0"))
    
    # integrity_hash مفهرس للتحقق من سلامة البيانات في أي لحظة
    integrity_hash = db.Column(db.String(64), nullable=True, index=True)

    # [Properties...] (نفس المنطق المعتمد للأمان)

    def generate_integrity_hash(self):
        data = f"{self.balance_sar}{self.balance_yer}{self.balance_usd}"
        return hashlib.sha256(data.encode()).hexdigest()

    def update_balance(self, sar_delta=0, yer_delta=0, usd_delta=0):
        self.balance_sar += sar_delta
        self.balance_yer += yer_delta
        self.balance_usd += usd_delta
        self.integrity_hash = self.generate_integrity_hash()

class VaultTransaction(db.Model):
    __tablename__ = 'vault_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    _amount = db.Column(db.String(255), nullable=False)
    
    # ⚡ فهارس للتدقيق المالي السريع
    currency = db.Column(db.String(3), nullable=False, index=True)
    transaction_type = db.Column(db.String(50), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # ⚡ فهرسة معرفات الربط لسرعة تتبع العمليات
    admin_id = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=True, index=True)
    reference_id = db.Column(db.String(100), nullable=True, index=True)

    @property
    def amount(self): 
        val = AESCipher.decrypt(self._amount)
        return float(val) if val else 0.0
    
    @amount.setter
    def amount(self, value): 
        self._amount = AESCipher.encrypt(str(value))
