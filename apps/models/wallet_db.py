# -*- coding: utf-8 -*-
# 📂 apps/models/wallet_db.py

from datetime import datetime
from apps.extensions import db


class SupplierWallet(db.Model):
    """نموذج المحفظة المالية الذكية للموردين - يدعم الترقيم النمطي WEL-963X والعملة بالريال السعودي فقط"""
    __tablename__ = 'supplier_wallets'

    # [فهرسة متقدمة]: لسرعة الاستعلامات والبحث
    __table_args__ = (
        db.Index('idx_wallet_code', 'wallet_code'),
        db.Index('idx_wallet_supplier_id', 'supplier_id'),
        db.Index('idx_wallet_status', 'is_active'),
        {'extend_existing': True}
    )

    # المعرفات الأساسية
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id', ondelete='CASCADE'), nullable=False, unique=True)
    wallet_code = db.Column(db.String(50), unique=True, nullable=True)  # الترقيم النمطي مثل WEL-9631
    
    # تفاصيل الحساب المالي (العملة ريال سعودي SAR حصراً)
    balance = db.Column(db.Numeric(12, 2), default=0.00, nullable=False)
    currency = db.Column(db.String(10), default='SAR', nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # تواريخ المتابعة
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقة مع نموذج المورد (تحميل كسول lazy='select' وتجنب الاستيراد الدائري)
    supplier = db.relationship('Supplier', back_populates='wallet', uselist=False, lazy='select')

    def __init__(self, **kwargs):
        """تثبيت العملة حصراً على الريال السعودي SAR بغض النظر عن المدخلات"""
        kwargs['currency'] = 'SAR'
        super().__init__(**kwargs)

    def to_dict(self):
        """تحويل المحفظة إلى قاموس آمن للاستخدام في APIs"""
        return {
            'id': self.id,
            'supplier_id': self.supplier_id,
            'wallet_code': self.wallet_code,
            'balance': float(self.balance) if self.balance is not None else 0.00,
            'currency': self.currency,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f"<SupplierWallet {self.wallet_code or self.id}: {self.balance} {self.currency}>"
