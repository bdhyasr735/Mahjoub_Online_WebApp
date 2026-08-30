# -*- coding: utf-8 -*-
# 📂 apps/models/wallet_db.py

from datetime import datetime
from apps.extensions import db


class SupplierWallet(db.Model):
    __tablename__ = 'supplier_wallets'

    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id', ondelete='CASCADE'), nullable=False, unique=True)
    wallet_code = db.Column(db.String(50), unique=True, nullable=False)
    balance = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(10), default='SAR')
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    supplier = db.relationship('Supplier', back_populates='wallet')

    def to_dict(self):
        return {
            'id': self.id,
            'supplier_id': self.supplier_id,
            'wallet_code': self.wallet_code,
            'balance': self.balance,
            'currency': self.currency,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<SupplierWallet {self.id}: {self.wallet_code}>"
