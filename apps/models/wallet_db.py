# coding: utf-8
import os
from apps.extensions import db
from apps.utils.security import AESCipher
from sqlalchemy import text, inspect

# تهيئة المشفر
cipher = AESCipher(os.getenv('ENCRYPTION_KEY', 'your-32-byte-key-here-must-be-secure'))

class SupplierWallet(db.Model):
    __tablename__ = 'supplier_wallets'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    supplier_id = db.Column(db.String(50), db.ForeignKey('suppliers.sovereign_id'), nullable=False, unique=True)
    wallet_code = db.Column(db.String(50), nullable=False, unique=True)
    
    # الأعمدة المشفرة (استخدمنا nullable=True لضمان عدم حدوث خطأ عند الإنشاء الأول)
    _yer_total = db.Column(db.String(255), default=cipher.encrypt("0.00"))
    _sar_total = db.Column(db.String(255), default=cipher.encrypt("0.00"))
    _usd_total = db.Column(db.String(255), default=cipher.encrypt("0.00"))
    
    status = db.Column(db.String(20), default='نشطة', nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now(), nullable=False)

    transactions = db.relationship('WalletTransaction', backref='wallet', lazy=True, cascade="all, delete-orphan")

    # --- خصائص التشفير ---
    @property
    def yer_total(self): return float(cipher.decrypt(self._yer_total))
    @yer_total.setter
    def yer_total(self, val): self._yer_total = cipher.encrypt(str(val))

    @property
    def sar_total(self): return float(cipher.decrypt(self._sar_total))
    @sar_total.setter
    def sar_total(self, val): self._sar_total = cipher.encrypt(str(val))

    @property
    def usd_total(self): return float(cipher.decrypt(self._usd_total))
    @usd_total.setter
    def usd_total(self, val): self._usd_total = cipher.encrypt(str(val))

# --- دالة الإصلاح التلقائي ---
def check_and_fix_table():
    with db.engine.connect() as conn:
        inspector = inspect(db.engine)
        columns = [c['name'] for c in inspector.get_columns('supplier_wallets')]
        for col in ['_yer_total', '_sar_total', '_usd_total']:
            if col not in columns:
                conn.execute(text(f"ALTER TABLE supplier_wallets ADD COLUMN {col} VARCHAR(255) DEFAULT '{cipher.encrypt('0.00')}'"))
        conn.commit()

# تنفيذ الإصلاح مباشرة عند تحميل الموديل
try:
    check_and_fix_table()
except:
    pass
