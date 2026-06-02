# coding: utf-8
import os
from apps.extensions import db
from apps.utils import AESCipher

# جلب المفتاح من البيئة (تأكد من إضافته في إعدادات Render)
encryption_key = os.getenv('ENCRYPTION_KEY')

if not encryption_key:
    print("⚠️ تحذير: لم يتم العثور على ENCRYPTION_KEY في البيئة! تم استخدام مفتاح افتراضي.")
    encryption_key = '00000000000000000000000000000000'

cipher = AESCipher(encryption_key)

class Wallet(db.Model):
    __tablename__ = 'supplier_wallets'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    supplier_id = db.Column(db.String(50), db.ForeignKey('suppliers.sovereign_id'), nullable=False, unique=True)
    wallet_code = db.Column(db.String(50), nullable=False, unique=True)
    
    # حقول مشفرة - تم ضبط الـ default ليعتمد على التشفير مباشرة
    _yer_total = db.Column(db.String(255), default=lambda: cipher.encrypt("0.0"))
    _sar_total = db.Column(db.String(255), default=lambda: cipher.encrypt("0.0"))
    _usd_total = db.Column(db.String(255), default=lambda: cipher.encrypt("0.0"))
    
    status = db.Column(db.String(20), default='نشطة', nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp(), nullable=False)

    transactions = db.relationship('WalletTransaction', backref='wallet', lazy=True, cascade="all, delete-orphan")

    # الخصائص (Properties) لفك التشفير التلقائي
    @property
    def yer_total(self): 
        try:
            return float(cipher.decrypt(self._yer_total))
        except Exception:
            return 0.0

    @yer_total.setter
    def yer_total(self, val):
        self._yer_total = cipher.encrypt(str(val))

    @property
    def sar_total(self): 
        try:
            return float(cipher.decrypt(self._sar_total))
        except Exception:
            return 0.0

    @sar_total.setter
    def sar_total(self, val):
        self._sar_total = cipher.encrypt(str(val))

    @property
    def usd_total(self): 
        try:
            return float(cipher.decrypt(self._usd_total))
        except Exception:
            return 0.0

    @usd_total.setter
    def usd_total(self, val):
        self._usd_total = cipher.encrypt(str(val))


class WalletTransaction(db.Model):
    __tablename__ = 'wallet_transactions'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('supplier_wallets.id'), nullable=False)
    
    tx_code = db.Column(db.String(60), unique=True, nullable=False)
    tx_type = db.Column(db.String(30), nullable=False) 
    currency = db.Column(db.String(10), nullable=False)
    
    _amount = db.Column(db.String(255), nullable=True)
    _profit_margin = db.Column(db.String(255), nullable=True)
    _notes = db.Column(db.String(500), nullable=True)
    
    # أعمدة الهجرة (Legacy Columns) لدعم البيانات القديمة
    legacy_amount = db.Column('amount', db.String(255), nullable=True)
    legacy_profit_margin = db.Column('profit_margin', db.String(255), nullable=True)
    legacy_notes = db.Column('notes', db.Text, nullable=True)
    
    status = db.Column(db.String(20), default='ناجحة', nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)

    @property
    def amount(self): 
        try:
            if self._amount:
                return float(cipher.decrypt(self._amount))
            return float(self.legacy_amount) if self.legacy_amount else 0.0
        except Exception:
            return 0.0

    @amount.setter
    def amount(self, val):
        self._amount = cipher.encrypt(str(val))

    @property
    def profit_margin(self): 
        try: 
            if self._profit_margin:
                return float(cipher.decrypt(self._profit_margin))
            return float(self.legacy_profit_margin) if self.legacy_profit_margin else 0.0
        except Exception:
            return 0.0

    @profit_margin.setter
    def profit_margin(self, val):
        self._profit_margin = cipher.encrypt(str(val))

    @property
    def notes(self): 
        try: 
            if self._notes:
                return cipher.decrypt(self._notes)
            return str(self.legacy_notes) if self.legacy_notes else ""
        except Exception:
            return ""

    @notes.setter
    def notes(self, val):
        self._notes = cipher.encrypt(str(val))
