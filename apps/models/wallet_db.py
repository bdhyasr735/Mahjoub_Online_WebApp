# coding: utf-8
# 📂 apps/models/wallet_db.py

import os
import base64
from datetime import datetime
from decimal import Decimal
from cryptography.fernet import Fernet
from sqlalchemy import event, select, update
from apps.extensions import db


class SupplierWallet(db.Model):
    """محفظة الموردين: الأرصدة والبيانات المشفرة بأعلى معايير الأمان."""
    __tablename__ = 'supplier_wallets'

    # [فهرسة استراتيجية]: دمج الحقول الأكثر طلباً في فهارس مركبة
    __table_args__ = (
        db.Index('idx_wall_lookup', 'supplier_id', 'wallet_code'), # بحث سريع عن المحفظة
        db.Index('idx_wall_activity', 'updated_at'),             # تتبع آخر تحديث
        {'extend_existing': True}
    )

    id = db.Column(db.Integer, primary_key=True)
    wallet_code = db.Column(db.String(50), unique=True, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False, unique=True)

    # أرصدة العملات
    balance_yer = db.Column(db.Numeric(18, 2), default=0.00)
    balance_usd = db.Column(db.Numeric(18, 2), default=0.00)
    balance_sar = db.Column(db.Numeric(18, 2), default=0.00)
    balance_pending = db.Column(db.Numeric(18, 2), default=0.00)
    total_withdrawn = db.Column(db.Numeric(18, 2), default=0.00)

    # [التشفير السيادي]: تفاصيل البنك محمية بـ Fernet
    _bank_details_enc = db.Column(db.String(500), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقات
    supplier = db.relationship('Supplier', back_populates='wallet', lazy='joined')
    transactions = db.relationship('WalletTransaction', back_populates='wallet', cascade="all, delete-orphan", lazy='selectin')

    # --- نظام التشفير الموحد ---
    @staticmethod
    def _get_fernet():
        """جلب كائن التشفير مع ضمان مفتاح Fernet صحيح (32-byte)."""
        key = os.environ.get('ENCRYPTION_KEY')
        if not key:
            key = 'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8V='
        
        try:
            return Fernet(key.encode('utf-8'))
        except Exception:
            b64_key = base64.urlsafe_b64encode(key.encode('utf-8')[:32].ljust(32, b'0'))
            return Fernet(b64_key)

    @property
    def bank_details(self):
        """فك تشفير تفاصيل الحساب البنكي."""
        if not self._bank_details_enc:
            return None
        try:
            return self._get_fernet().decrypt(self._bank_details_enc.encode('utf-8')).decode('utf-8')
        except Exception:
            return None

    @bank_details.setter
    def bank_details(self, value):
        if value:
            self._bank_details_enc = self._get_fernet().encrypt(str(value).encode('utf-8')).decode('utf-8')
        else:
            self._bank_details_enc = None

    def to_dict(self):
        return {
            'id': self.id,
            'wallet_code': self.wallet_code,
            'supplier_id': self.supplier_id,
            'balance_yer': float(self.balance_yer or 0.0),
            'balance_usd': float(self.balance_usd or 0.0),
            'balance_sar': float(self.balance_sar or 0.0),
            'bank_details': self.bank_details,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class WalletTransaction(db.Model):
    """سجل الحركات المالية الموحد مع أفضل فهرسة للأداء العالي."""
    __tablename__ = 'wallet_transactions'

    # [أفضل فهرسة عالمية]: الفهرس المركب (wallet_id, created_at) يجعل الاستعلام عن كشف حساب أي محفظة فورياً
    __table_args__ = (
        db.Index('idx_trans_wallet_history', 'wallet_id', 'created_at'),
        db.Index('idx_trans_lookup', 'voucher_number', 'reference_number'),
        db.Index('idx_trans_status_type', 'status', 'trans_type'),
        {'extend_existing': True}
    )

    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('supplier_wallets.id'), nullable=False)
    owner_type = db.Column(db.String(20), default='supplier')
    owner_id = db.Column(db.Integer, nullable=False)

    trans_type = db.Column(db.String(30), nullable=False)
    status = db.Column(db.String(30), default='completed') 
    amount = db.Column(db.Numeric(18, 2), nullable=False)
    currency = db.Column(db.String(5), nullable=False, default='SAR')
    balance_before = db.Column(db.Numeric(18, 2), nullable=False)
    balance_after = db.Column(db.Numeric(18, 2), nullable=False)
    
    description = db.Column(db.String(255))
    reference_number = db.Column(db.String(50), unique=True, nullable=True)
    voucher_number = db.Column(db.String(30), unique=True, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    wallet = db.relationship('SupplierWallet', back_populates='transactions', lazy='joined')

    def to_dict(self):
        return {
            'id': self.id,
            'trans_type': self.trans_type,
            'status': self.status,
            'amount': float(self.amount or 0.0),
            'reference_number': self.reference_number,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# --- مشغل الأحداث (Engine) للتسوية التلقائية ---
@event.listens_for(WalletTransaction, 'before_insert')
def process_wallet_transaction_before_insert(mapper, connection, target):
    """توليد الأرقام المرجعية وحساب الأرصدة لحظياً."""
    
    # 1. إنشاء رقم المرجع (Ref)
    if not target.reference_number:
        date_str = datetime.utcnow().strftime('%Y%m%d')
        # بحث عن آخر رقم مرجعي لهذه المحفظة في هذا اليوم
        last_ref = connection.execute(
            select(WalletTransaction.reference_number)
            .where(WalletTransaction.wallet_id == target.wallet_id)
            .where(WalletTransaction.reference_number.like(f"%{date_str}%"))
            .order_by(WalletTransaction.id.desc())
            .limit(1)
        ).scalar()
        
        seq = (int(last_ref.split('-')[-1]) + 1) if last_ref else 1
        target.reference_number = f"TRX-{target.wallet_id}-{date_str}-{seq:04d}"

    # 2. حساب الأرصدة (Balance Logic)
    wallet_table = SupplierWallet.__table__
    wallet_row = connection.execute(
        select(wallet_table).where(wallet_table.c.id == target.wallet_id)
    ).mappings().first()

    if wallet_row:
        attr = f'balance_{(target.currency or "sar").lower()}'
        current_bal = Decimal(str(wallet_row.get(attr, 0)))
        
        target.balance_before = current_bal
        is_credit = target.trans_type in ['credit', 'sale_revenue', 'deposit', 'refund', 'adjustment_credit']
        target.balance_after = (current_bal + Decimal(str(target.amount))) if is_credit else (current_bal - Decimal(str(target.amount)))

        # تحديث المحفظة مباشرة
        connection.execute(
            update(wallet_table)
            .where(wallet_table.c.id == target.wallet_id)
            .values({attr: target.balance_after, 'updated_at': datetime.utcnow()})
        )
