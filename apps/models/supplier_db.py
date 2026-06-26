# coding: utf-8
# 📂 apps/models/supplier_db.py

import os
from datetime import datetime
from cryptography.fernet import Fernet
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import event, update
from apps.extensions import db

class Supplier(db.Model, UserMixin):
    __tablename__ = 'suppliers'
    
    # [صمام الأمان]: فهرسة مسمّاة ومنع تكرار التعريف
    __table_args__ = (
        db.Index('idx_sup_username', 'username'),
        db.Index('idx_sup_code', 'supplier_code'),
        db.Index('idx_sup_trade', 'trade_name'),
        db.Index('idx_sup_phone', 'search_phone'),
        db.Index('idx_sup_status', 'status'),
        db.Index('idx_sup_rank', 'rank'),
        db.Index('idx_sup_created', 'created_at'),
        {'extend_existing': True}
    )

    # الأعمدة
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    supplier_code = db.Column(db.String(50), unique=True, nullable=True)
    trade_name = db.Column(db.String(150), nullable=True)
    _phone_enc = db.Column(db.String(255), nullable=False)
    search_phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='active')
    rank = db.Column(db.String(20), default='bronze')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    # [المسار الكامل]: لمنع خطأ Multiple classes found
    supplier_profile = db.relationship('apps.models.supplier_profile_db.SupplierProfile', back_populates='supplier', uselist=False, cascade="all, delete-orphan")
    wallet = db.relationship('apps.models.wallet_db.SupplierWallet', back_populates='supplier', uselist=False, cascade="all, delete-orphan")
    orders = db.relationship('apps.models.orders_db.Order', back_populates='supplier', cascade="all, delete-orphan")
    financials = db.relationship('apps.models.financials_db.OrderFinancial', back_populates='supplier', cascade="all, delete-orphan")
    staff_members = db.relationship('apps.models.supplier_staff_db.SupplierStaff', back_populates='supplier', cascade="all, delete-orphan")

    # --- نظام التشفير (AES) ---
    @staticmethod
    def _get_key():
        return os.environ.get('ENCRYPTION_KEY', 'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8Vq=').encode()

    @property
    def phone(self):
        try:
            return Fernet(self._get_key()).decrypt(self._phone_enc.encode()).decode()
        except: return None

    @phone.setter
    def phone(self, value):
        self._phone_enc = Fernet(self._get_key()).encrypt(str(value).encode()).decode()
        self.search_phone = str(value)[:20]

    # [التشفير السيادي]: ترقية كلمة المرور لـ PBKDF2
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Supplier {self.username}>'

# --- نظام إنشاء المحفظة وتحديث الكود تلقائياً ---
@event.listens_for(Supplier, 'after_insert')
def receive_after_insert(mapper, connection, target):
    from apps.models.wallet_db import SupplierWallet
    
    new_supplier_code = f"MAH-SUP963{target.id}"
    connection.execute(
        update(Supplier).where(Supplier.id == target.id).values(supplier_code=new_supplier_code)
    )
    
    new_wallet = SupplierWallet(
        wallet_code=f"MAH-WEL963{target.id}",
        supplier_id=target.id,
        balance_yer=0.00, balance_usd=0.00, balance_sar=0.00, balance_pending=0.00
    )
    
    session = db.session.object_session(target)
    if session:
        session.add(new_wallet)
