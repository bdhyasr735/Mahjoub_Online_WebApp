# coding: utf-8
# 📂 apps/models/wallet_db.py

import os
import base64
from datetime import datetime
from decimal import Decimal
from cryptography.fernet import Fernet
from sqlalchemy import event, func, select
from apps.extensions import db


class SupplierWallet(db.Model):
    """محفظة الموردين: الأرصدة والبيانات المشفرة."""
    __tablename__ = 'supplier_wallets'

    # [فهرسة الأداء]: للوصول السريع للأرصدة في العمليات المالية
    __table_args__ = (
        db.Index('idx_wall_code', 'wallet_code'),
        db.Index('idx_wall_supplier_id', 'supplier_id'),
        db.Index('idx_wall_updated', 'updated_at'),
        {'extend_existing': True}
    )

    id = db.Column(db.Integer, primary_key=True)
    wallet_code = db.Column(db.String(50), unique=True, nullable=False)

    # الربط الرقمي مع المورد
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False, unique=True)

    # أرصدة العملات (بدون تشفير لسرعة الحسابات والفرز)
    balance_yer = db.Column(db.Numeric(18, 2), default=0.00)
    balance_usd = db.Column(db.Numeric(18, 2), default=0.00)
    balance_sar = db.Column(db.Numeric(18, 2), default=0.00)
    balance_pending = db.Column(db.Numeric(18, 2), default=0.00)
    total_withdrawn = db.Column(db.Numeric(18, 2), default=0.00)

    # [تشفير حساس] - تفاصيل البنك محمية بـ Fernet
    _bank_details_enc = db.Column(db.String(500), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # [العلاقات الأسرع والأكثر أماناً]:
    supplier = db.relationship('Supplier', back_populates='wallet', lazy='joined')
    transactions = db.relationship('WalletTransaction', back_populates='wallet', cascade="all, delete-orphan", lazy='selectin')

    @staticmethod
    def _get_fernet():
        """جلب كائن التشفير مع ضمان مفتاح Fernet صحيح بحجم 32 بايت."""
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
            fernet = self._get_fernet()
            return fernet.decrypt(self._bank_details_enc.encode('utf-8')).decode('utf-8')
        except Exception:
            return None

    @bank_details.setter
    def bank_details(self, value):
        """تشفير تفاصيل الحساب البنكي قبل الحفظ."""
        if value:
            fernet = self._get_fernet()
            self._bank_details_enc = fernet.encrypt(str(value).encode('utf-8')).decode('utf-8')
        else:
            self._bank_details_enc = None

    @property
    def default_currency(self):
        return "SAR"

    def to_dict(self):
        """تحويل بيانات المحفظة إلى قاموس آمن للاستخدام في الواجهات والـ APIs."""
        return {
            'id': self.id,
            'wallet_code': self.wallet_code,
            'supplier_id': self.supplier_id,
            'balance_yer': float(self.balance_yer or 0.0),
            'balance_usd': float(self.balance_usd or 0.0),
            'balance_sar': float(self.balance_sar or 0.0),
            'balance_pending': float(self.balance_pending or 0.0),
            'total_withdrawn': float(self.total_withdrawn or 0.0),
            'bank_details': self.bank_details,
            'default_currency': self.default_currency,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<SupplierWallet {self.wallet_code} | SAR: {self.balance_sar} | Pending: {self.balance_pending}>'


class WalletTransaction(db.Model):
    """سجل الحركات المالية الموحد."""
    __tablename__ = 'wallet_transactions'

    __table_args__ = (
        db.Index('idx_trans_wallet', 'wallet_id'),
        db.Index('idx_trans_date', 'created_at'),
        db.Index('idx_trans_type', 'trans_type'),
        db.Index('idx_trans_status', 'status'),
        db.Index('idx_trans_owner', 'owner_type', 'owner_id'),
        db.Index('idx_trans_voucher', 'voucher_number'),
        {'extend_existing': True}
    )

    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('supplier_wallets.id'), nullable=False)
    owner_type = db.Column(db.String(20), default='supplier')
    owner_id = db.Column(db.Integer, nullable=False)

    trans_type = db.Column(db.String(30), nullable=False)  # credit, debit, withdrawal, etc.
    status = db.Column(db.String(30), default='completed', index=True) # completed, pending, cancelled
    source_type = db.Column(db.String(20), default='manual')
    
    amount = db.Column(db.Numeric(18, 2), nullable=False)
    currency = db.Column(db.String(5), nullable=False, default='SAR')
    balance_before = db.Column(db.Numeric(18, 2), nullable=False)
    balance_after = db.Column(db.Numeric(18, 2), nullable=False)
    
    description = db.Column(db.String(255))
    reference_number = db.Column(db.String(50))
    related_order_id = db.Column(db.String(50), nullable=True)
    voucher_number = db.Column(db.String(30), unique=True, nullable=True)
    
    # حقول تفاصيل السحب الإضافية للتوافق التام مع مسارات السحب
    payout_method = db.Column(db.String(50), nullable=True)
    account_details = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, nullable=True)

    # جلب المحفظة مع المعاملة
    wallet = db.relationship('SupplierWallet', back_populates='transactions', lazy='joined')

    # --- توافقية الأسماء لتجنب أي أخطاء في الـ Routes ---
    @property
    def transaction_type(self):
        return self.trans_type

    @transaction_type.setter
    def transaction_type(self, value):
        self.trans_type = value

    @property
    def trx_type(self):
        return self.trans_type

    @trx_type.setter
    def trx_type(self, value):
        self.trans_type = value

    @property
    def default_currency(self):
        return "SAR"

    def to_dict(self):
        """تحويل تفاصيل المعاملة المالية إلى قاموس آمن للاستخدام في APIs."""
        return {
            'id': self.id,
            'wallet_id': self.wallet_id,
            'owner_type': self.owner_type,
            'owner_id': self.owner_id,
            'trans_type': self.trans_type,
            'transaction_type': self.trans_type,
            'status': self.status,
            'source_type': self.source_type,
            'amount': float(self.amount or 0.0),
            'currency': self.currency,
            'balance_before': float(self.balance_before or 0.0),
            'balance_after': float(self.balance_after or 0.0),
            'description': self.description,
            'reference_number': self.reference_number,
            'related_order_id': self.related_order_id,
            'voucher_number': self.voucher_number,
            'payout_method': self.payout_method,
            'account_details': self.account_details,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<WalletTransaction {self.voucher_number} | Type: {self.trans_type} | Status: {self.status} | {self.currency} {self.amount}>'


# --- مشغل الأحداث للتسوية التلقائية والحفاظ على دقة الأرصدة ---
@event.listens_for(WalletTransaction, 'before_insert')
def process_wallet_transaction_before_insert(mapper, connection, target):
    """
    يقوم بحساب رقم السند تلقائياً واحتساب الرصيد السابق واللاحق وتحديث جدول المحفظة
    مباشرة بدقة متناهية دون السقوط في فخ أخطاء ORM.
    """
    # 1. إنشاء رقم السند الآلي عند عدم وجوده
    if not target.voucher_number:
        last_num = 12327
        last_trans_stmt = (
            select(WalletTransaction.voucher_number)
            .where(WalletTransaction.voucher_number.isnot(None))
            .order_by(WalletTransaction.id.desc())
            .limit(1)
        )
        last_trans = connection.execute(last_trans_stmt).scalar()
        if last_trans and '-' in last_trans:
            try:
                last_num = int(last_trans.split('-')[-1])
            except (ValueError, IndexError):
                pass
        target.voucher_number = f"MJ-2026-{last_num + 1:07d}"

    # 2. حساب balance_before و balance_after وتحديث جدول المحفظة تلقائياً
    if target.balance_before is None or target.balance_after is None:
        wallet_table = SupplierWallet.__table__
        
        wallet_row = connection.execute(
            select(wallet_table).where(wallet_table.c.id == target.wallet_id)
        ).mappings().first()

        if wallet_row:
            curr_code = (target.currency or 'SAR').lower()
            attr = f'balance_{curr_code}' if curr_code in ['sar', 'yer', 'usd'] else 'balance_sar'
            
            current_balance = Decimal(str(wallet_row.get(attr) or 0))
            amount_dec = Decimal(str(target.amount or 0))

            target.balance_before = current_balance

            CREDIT_TYPES = {'credit', 'adjustment_credit', 'sale_revenue', 'deposit', 'refund'}
            
            if target.trans_type in CREDIT_TYPES:
                target.balance_after = current_balance + amount_dec
            else:
                target.balance_after = current_balance - amount_dec

            connection.execute(
                db.update(wallet_table)
                .where(wallet_table.c.id == target.wallet_id)
                .values({
                    attr: target.balance_after,
                    'updated_at': datetime.utcnow()
                })
            )
