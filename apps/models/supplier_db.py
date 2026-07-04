# coding: utf-8
# 📂 apps/models/suppliers_db.py

import os
from datetime import datetime
from cryptography.fernet import Fernet
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import event, update, Table, MetaData, Column, Integer, String, Float
from apps.extensions import db

class Supplier(db.Model, UserMixin):
    __tablename__ = 'suppliers'
    
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

    # الأعمدة الأساسية
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    supplier_code = db.Column(db.String(50), unique=True, nullable=True)
    owner_name = db.Column(db.String(150), nullable=True) 
    trade_name = db.Column(db.String(150), nullable=True)
    
    # التشفير والبحث (تشفير رقم الهاتف)
    _phone_enc = db.Column(db.String(255), nullable=False) 
    search_phone = db.Column(db.String(20))
    
    # الإعدادات والحالة
    password_hash = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='active')
    rank = db.Column(db.String(20), default='bronze')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    # العلاقات (Relationships)
    supplier_profile = db.relationship('SupplierProfile', back_populates='supplier', uselist=False, cascade="all, delete-orphan")
    wallet = db.relationship('SupplierWallet', back_populates='supplier', uselist=False, cascade="all, delete-orphan")
    orders = db.relationship('Order', back_populates='supplier', cascade="all, delete-orphan")
    financials = db.relationship('OrderFinancial', back_populates='supplier', cascade="all, delete-orphan")
    staff_members = db.relationship('SupplierStaff', back_populates='supplier', cascade="all, delete-orphan")

    # --- نظام التشفير (AES) ---
    @staticmethod
    def _get_key():
        key = os.environ.get('ENCRYPTION_KEY', 'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8Vq=')
        return key.encode()

    @property
    def phone(self):
        try:
            return Fernet(self._get_key()).decrypt(self._phone_enc.encode()).decode()
        except: return None

    @phone.setter
    def phone(self, value):
        if value:
            self._phone_enc = Fernet(self._get_key()).encrypt(str(value).encode()).decode()
            self.search_phone = str(value)[-9:]

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# --- نظام المحرك التلقائي (Auto-Discovery & Auto-Creation) ---
@event.listens_for(Supplier, 'after_insert')
def receive_after_insert(mapper, connection, target):
    # 1. تحديث الكود الخاص بالمورد
    new_code = f"MAH-SUP963{target.id}"
    connection.execute(
        update(Supplier).where(Supplier.id == target.id).values(supplier_code=new_code)
    )
    
    metadata = MetaData()
    
    # 2. إنشاء المحفظة تلقائياً
    wallets_table = Table('supplier_wallets', metadata, 
                          Column('id', Integer, primary_key=True),
                          Column('wallet_code', String(50)),
                          Column('supplier_id', Integer),
                          autoload_with=connection)
    
    connection.execute(
        wallets_table.insert().values(
            wallet_code=f"MAH-WEL963{target.id}",
            supplier_id=target.id
        )
    )

    # 3. إنشاء المالك (Owner) تلقائياً في جدول الموظفين
    staff_table = Table('supplier_staff', metadata,
                        Column('id', Integer, primary_key=True),
                        Column('supplier_id', Integer),
                        Column('username', String(100)),
                        Column('phone', String(20)),
                        Column('password_hash', String(255)),
                        Column('role', String(50)),
                        autoload_with=connection)
    
    # كلمة مرور افتراضية للمالك (يمكن للمورد تغييرها لاحقاً)
    default_pw = generate_password_hash("Admin123!", method='pbkdf2:sha256')
    
    connection.execute(
        staff_table.insert().values(
            supplier_id=target.id,
            username=target.username,
            phone=target.phone, 
            password_hash=default_pw,
            role='owner' 
        )
    )
