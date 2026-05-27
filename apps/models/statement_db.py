# coding: utf-8
# 📂 apps/models/statement_db.py

import os
from apps.extensions import db
from datetime import datetime
from apps.utils.security import AESCipher

# تهيئة مشفر البيانات
cipher = AESCipher(os.getenv('ENCRYPTION_KEY', 'your-32-byte-key-here-must-be-secure'))

class SupplierStatement(db.Model):
    """
    نموذج العمليات المحاسبية للموردين - محصن ومشفر
    """
    __tablename__ = 'supplier_statements'
    
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # حقول مشفرة (تخزين Ciphertext)
    _description = db.Column(db.String(500), nullable=True) 
    _debit = db.Column(db.String(255), default=cipher.encrypt("0.0"))
    _credit = db.Column(db.String(255), default=cipher.encrypt("0.0"))
    _running_balance = db.Column(db.String(255), nullable=False)
    
    currency = db.Column(db.String(10), default='USD')

    # --- خصائص التشفير (Getters & Setters) ---

    @property
    def description(self): return cipher.decrypt(self._description) if self._description else ""
    @description.setter
    def description(self, value): self._description = cipher.encrypt(str(value))

    @property
    def debit(self): return float(cipher.decrypt(self._debit))
    @debit.setter
    def debit(self, value): self._debit = cipher.encrypt(str(value))

    @property
    def credit(self): return float(cipher.decrypt(self._credit))
    @credit.setter
    def credit(self, value): self._credit = cipher.encrypt(str(value))

    @property
    def running_balance(self): return float(cipher.decrypt(self._running_balance))
    @running_balance.setter
    def running_balance(self, value): self._running_balance = cipher.encrypt(str(value))

    def __repr__(self):
        return f'<SupplierStatement {self.id} - Supplier ID: {self.supplier_id}>'
