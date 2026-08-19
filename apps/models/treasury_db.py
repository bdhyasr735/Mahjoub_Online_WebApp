# coding: utf-8
# 📂 apps/models/treasury_db.py

import os
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from apps.extensions import db

class TreasuryEntry(db.Model):
    """Central Treasury Ledger - Immutable financial audit log (SAR)"""
    __tablename__ = 'treasury_entries'

    __table_args__ = (
        db.Index('idx_treasury_type_date', 'entry_type', 'created_at'),
        db.Index('idx_treasury_owner', 'owner_type', 'owner_id'),
        db.Index('idx_treasury_ref', 'reference_number'),
        db.Index('idx_treasury_voucher', 'voucher_number'),
        db.Index('idx_treasury_order', 'order_id'), # إضافة لسرعة الربط
        {'extend_existing': True}
    )

    id = db.Column(db.Integer, primary_key=True)
    entry_type = db.Column(db.String(50), nullable=False) 
    amount = db.Column(db.Numeric(18, 2), nullable=False, default=0.00)
    currency = db.Column(db.String(10), default='SAR', nullable=False)

    order_id = db.Column(db.String(100), db.ForeignKey('orders.id'), nullable=True)
    reference_number = db.Column(db.String(80), nullable=True) 
    voucher_number = db.Column(db.String(50), unique=True, nullable=True)  
    
    owner_type = db.Column(db.String(20), nullable=False) 
    owner_id = db.Column(db.Integer, nullable=False)
    
    _description_enc = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # --- Encryption System ---
    @staticmethod
    def _get_key():
        key = os.environ.get('ENCRYPTION_KEY', 'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8V=')
        return key.encode()

    @property
    def description(self):
        if not self._description_enc: return None
        try:
            return Fernet(self._get_key()).decrypt(self._description_enc.encode()).decode()
        except: return None

    @description.setter
    def description(self, value):
        if value:
            self._description_enc = Fernet(self._get_key()).encrypt(str(value).encode()).decode()
        else:
            self._description_enc = None

    @property
    def owner_details(self):
        """Dynamic fetch with safe lazy loading to avoid import loops"""
        if self.owner_type == 'supplier':
            # استيراد محلي لتجنب تعارض الاستيراد
            from apps.models.supplier_db import Supplier
            from apps.models.wallet_db import SupplierWallet
            
            supplier = db.session.get(Supplier, self.owner_id)
            wallet = SupplierWallet.query.filter_by(supplier_id=self.owner_id).first()
            
            return {
                "owner_name": supplier.owner_name if supplier else "Unknown",
                "store_name": supplier.store_name if supplier else "Unknown",
                "supplier_code": supplier.supplier_code if supplier else f"SUP-{self.owner_id}",
                "wallet_code": wallet.wallet_code if wallet else "N/A"
            }
        return {"owner_name": self.owner_type, "store_name": "-", "supplier_code": "-", "wallet_code": "-"}

    @property
    def formatted_time(self):
        return (self.created_at + timedelta(hours=3)).strftime('%Y-%m-%d | %I:%M:%S %p') if self.created_at else "-"

    def to_dict(self):
        return {
            'id': self.id,
            'entry_type': self.entry_type,
            'amount': float(self.amount),
            'order_id': self.order_id,
            'voucher': self.voucher_number,
            'owner_info': self.owner_details,
            'description': self.description,
            'time': self.formatted_time
        }
