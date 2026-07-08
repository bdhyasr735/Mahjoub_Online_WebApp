# coding: utf-8
# 📂 apps/models/wallet_db.py

import os
from datetime import datetime
from decimal import Decimal
from cryptography.fernet import Fernet
from apps.extensions import db
from sqlalchemy import event, func, select

class SupplierWallet(db.Model):
    """محفظة الموردين: الأرصدة والبيانات المشفرة."""
    __tablename__ = 'supplier_wallets'

    # [فهرسة الأداء]: للوصول السريع للأرصدة
    __table_args__ = (
        db.Index('idx_wall_code', 'wallet_code'),
        db.Index('idx_wall_supplier_id', 'supplier_id'),
        db.Index('idx_wall_updated', 'updated_at'),
        {'extend_existing': True}
    )
    
    id = db.Column(db.Integer, primary_key=True)
    wallet_code = db.Column(db.String(50), unique=True, nullable=False)
    
    # الربط الرقمي الصحيح مع المورد
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False, unique=True)
    
    # أرصدة العملات
    balance_yer = db.Column(db.Numeric(18, 2), default=0.00) 
    balance_usd = db.Column(db.Numeric(18, 2), default=0.00) 
    balance_sar = db.Column(db.Numeric(18, 2), default=0.00) 
    balance_pending = db.Column(db.Numeric(18, 2), default=0.00)    
    total_withdrawn = db.Column(db.Numeric(18, 2), default=0.00)    
    
    # [تشفير حساس] - تفاصيل البنك محمية بـ Fernet
    _bank_details_enc = db.Column(db.String(500), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    supplier = db.relationship('Supplier', back_populates='wallet')
    transactions = db.relationship('WalletTransaction', back_populates='wallet', cascade="all, delete-orphan")

    @staticmethod
    def _get_key():
        key = os.environ.get('ENCRYPTION_KEY')
        return key.encode() if key else b'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8Vq='

    @property
    def bank_details(self):
        if not self._bank_details_enc: return None
        try:
            return Fernet(self._get_key()).decrypt(self._bank_details_enc.encode()).decode()
        except Exception: return None

    @bank_details.setter
    def bank_details(self, value):
        if value:
            self._bank_details_enc = Fernet(self._get_key()).encrypt(str(value).encode()).decode()
        else: 
            self._bank_details_enc = None

class WalletTransaction(db.Model):
    """سجل الحركات المالية الموحد."""
    __tablename__ = 'wallet_transactions'
    
    # [فهرسة الأداء]: للبحث في سجلات العمليات
    __table_args__ = (
        db.Index('idx_trans_wallet', 'wallet_id'),
        db.Index('idx_trans_date', 'created_at'),
        db.Index('idx_trans_type', 'trans_type'),
        db.Index('idx_trans_owner', 'owner_type', 'owner_id'),
        db.Index('idx_trans_voucher', 'voucher_number'),
        {'extend_existing': True}
    )

    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('supplier_wallets.id'), nullable=False)
    owner_type = db.Column(db.String(20), default='supplier') 
    owner_id = db.Column(db.Integer, nullable=False) # معرف المورد الرقمي
    
    trans_type = db.Column(db.String(20), nullable=False) 
    source_type = db.Column(db.String(20), default='manual')
    amount = db.Column(db.Numeric(18, 2), nullable=False)
    currency = db.Column(db.String(5), nullable=False)
    balance_before = db.Column(db.Numeric(18, 2), nullable=False)
    balance_after = db.Column(db.Numeric(18, 2), nullable=False)
    description = db.Column(db.String(255))
    reference_number = db.Column(db.String(50)) 
    related_order_id = db.Column(db.String(50), nullable=True) # معرف الطلب النصي
    voucher_number = db.Column(db.String(20), unique=True, nullable=True) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, nullable=True)

    wallet = db.relationship('SupplierWallet', back_populates='transactions')

# --- مشغل الأحداث (Event Listener) للتسوية التلقائية ---
@event.listens_for(WalletTransaction, 'before_insert')
def set_voucher_number(mapper, connection, target):
    """توليد رقم القسيمة وتحديث رصيد المحفظة تلقائياً عند إضافة حركة."""
    if not target.voucher_number:
        # توليد رقم تسلسلي فريد
        last_trans = connection.execute(
            select(func.max(WalletTransaction.voucher_number))
        ).scalar()
        
        last_num = 12327
        if last_trans and '-' in last_trans:
            try: last_num = int(last_trans.split('-')[-1])
            except: pass
        target.voucher_number = f"MJ-2026-{last_num + 1:07d}"

    # حساب وتحديث رصيد المحفظة
    if target.balance_before is None or target.balance_after is None:
        wallet = connection.execute(
            select(SupplierWallet).filter_by(id=target.wallet_id)
        ).scalar_one_or_none()
        
        if wallet:
            amount_dec = Decimal(str(target.amount or 0))
            attr = f'balance_{target.currency.lower()}'
            current = Decimal(str(getattr(wallet, attr, 0) or 0))
            
            target.balance_before = current
            
            # تحديد نوع الحركة وتأثيرها على الرصيد
            if target.trans_type in ['credit', 'adjustment_credit', 'sale_revenue']:
                target.balance_after = current + amount_dec
            else:
                target.balance_after = current - amount_dec
            
            setattr(wallet, attr, target.balance_after)
