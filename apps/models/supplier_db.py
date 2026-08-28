# coding: utf-8
# 📂 apps/models/wallet_db.py

from datetime import datetime
from apps.extensions import db


class SupplierWallet(db.Model):
    """نموذج محفظة المورد - مرتبطة بجدول الموردين وتدعم الترقيم النمطي WEL-963X"""
    __tablename__ = 'supplier_wallets'

    __table_args__ = (
        db.Index('idx_wallet_code', 'wallet_code'),
        db.Index('idx_wallet_supplier', 'supplier_id'),
        {'extend_existing': True}
    )

    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id', ondelete='CASCADE'), unique=True, nullable=False)
    wallet_code = db.Column(db.String(50), unique=True, nullable=True)
    
    # الأرصدة المالية
    balance = db.Column(db.Numeric(12, 2), default=0.00, nullable=False)
    locked_balance = db.Column(db.Numeric(12, 2), default=0.00, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقة العكسية مع المورد
    supplier = db.relationship('Supplier', back_populates='wallet', lazy='select')

    def to_dict(self):
        return {
            'id': self.id,
            'supplier_id': self.supplier_id,
            'wallet_code': self.wallet_code,
            'balance': float(self.balance),
            'locked_balance': float(self.locked_balance),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<SupplierWallet {self.wallet_code}: Balance={self.balance}>"
