# coding: utf-8
import os
from apps.extensions import db
from apps.utils.security import AESCipher

# تهيئة المشفر
cipher = AESCipher(os.getenv('ENCRYPTION_KEY', 'default-fallback-key-32-chars-long!'))

class SupplierWallet(db.Model):
    __tablename__ = 'supplier_wallets'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    supplier_id = db.Column(db.String(50), db.ForeignKey('suppliers.sovereign_id'), nullable=False, unique=True)
    wallet_code = db.Column(db.String(50), nullable=False, unique=True)
    
    _yer_total = db.Column(db.String(255), default=lambda: cipher.encrypt("0.00"))
    _sar_total = db.Column(db.String(255), default=lambda: cipher.encrypt("0.00"))
    _usd_total = db.Column(db.String(255), default=lambda: cipher.encrypt("0.00"))
    
    status = db.Column(db.String(20), default='نشطة', nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now(), nullable=False)

    transactions = db.relationship('WalletTransaction', backref='wallet', lazy=True, cascade="all, delete-orphan")

    @property
    def yer_total(self): 
        try: return float(cipher.decrypt(self._yer_total))
        except: return 0.0
    @yer_total.setter
    def yer_total(self, val): self._yer_total = cipher.encrypt(str(val))

    @property
    def sar_total(self): 
        try: return float(cipher.decrypt(self._sar_total))
        except: return 0.0
    @sar_total.setter
    def sar_total(self, val): self._sar_total = cipher.encrypt(str(val))

class WalletTransaction(db.Model):
    __tablename__ = 'wallet_transactions'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('supplier_wallets.id'), nullable=False)
    
    tx_code = db.Column(db.String(60), unique=True, nullable=False)
    tx_type = db.Column(db.String(30), nullable=False) 
    currency = db.Column(db.String(10), nullable=False)
    
    # 1. الأعمدة المشفرة الجديدة (بشرطة سفلية)
    _amount = db.Column(db.String(255), nullable=True)
    _profit_margin = db.Column(db.String(255), nullable=True)
    _notes = db.Column(db.Text, nullable=True)
    
    # 2. إضافة الأعمدة القديمة كـ Nullable لتجنب خطأ UndefinedColumn
    # (SQLAlchemy سيقوم بتجاهلهم إذا كانوا موجودين فعلياً في القاعدة أو يضيفهم كأعمدة وهمية)
    amount = db.Column(db.String(255), nullable=True)
    profit_margin = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    status = db.Column(db.String(20), default='ناجحة', nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now(), nullable=False)

    # --- الخصائص الذكية (تقرأ من الجديد، وإذا فشلت تقرأ من القديم) ---
    @property
    def amount(self): 
        try:
            # نحاول قراءة العمود الجديد أولاً
            if self._amount: return float(cipher.decrypt(self._amount))
            # ثم القديم
            if self.amount: return float(cipher.decrypt(self.amount))
            return 0.0
        except: return 0.0
    
    @amount.setter
    def amount(self, val): self._amount = cipher.encrypt(str(val))

    @property
    def profit_margin(self): 
        try: 
            if self._profit_margin: return float(cipher.decrypt(self._profit_margin))
            if self.profit_margin: return float(cipher.decrypt(self.profit_margin))
            return 0.0
        except: return 0.0
        
    @profit_margin.setter
    def profit_margin(self, val): self._profit_margin = cipher.encrypt(str(val))

    @property
    def notes(self): 
        try: 
            if self._notes: return cipher.decrypt(self._notes)
            if self.notes: return cipher.decrypt(self.notes)
            return ""
        except: return ""
        
    @notes.setter
    def notes(self, val): self._notes = cipher.encrypt(str(val))
