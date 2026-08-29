# -*- coding: utf-8 -*-
# 📂 apps/models/supplier_db.py

import os
from datetime import datetime
from cryptography.fernet import Fernet
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import event, update, select
from apps.extensions import db


class Supplier(db.Model, UserMixin):
    """نموذج المورد - يدعم التشفير السيادي المحكم والعلاقات والترقيم النمطي المتطابق SUP-963X / WEL-963X"""
    __tablename__ = 'suppliers'
    
    # [فهرسة متقدمة]: لضمان سرعة الاستعلامات والبحث
    __table_args__ = (
        db.Index('idx_sup_username', 'username'),
        db.Index('idx_sup_email', 'email'),
        db.Index('idx_sup_code', 'supplier_code'),
        db.Index('idx_sup_trade', 'trade_name'),
        db.Index('idx_sup_store', 'store_name'),
        db.Index('idx_sup_phone', 'search_phone'),
        db.Index('idx_sup_status', 'status'),
        db.Index('idx_sup_rank', 'rank'),
        db.Index('idx_sup_created', 'created_at'),
        {'extend_existing': True}
    )

    # المعرفات الأساسية
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)  # حقل البريد الإلكتروني للتسجيل
    supplier_code = db.Column(db.String(50), unique=True, nullable=True)
    owner_name = db.Column(db.String(150), nullable=True) 
    trade_name = db.Column(db.String(150), nullable=True)
    store_name = db.Column(db.String(150), nullable=True)  # حقل اسم المتجر الجديد
    
    # [التشفير السيادي]: رقم الهاتف مشفر بالكامل
    _phone_enc = db.Column(db.String(255), nullable=False) 
    search_phone = db.Column(db.String(20))
    
    # الأمن وإدارة الحساب
    password_hash = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='active')
    rank = db.Column(db.String(20), default='bronze')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    # العلاقات: باستخدام التحميل الكسول (lazy='select')
    supplier_profile = db.relationship('SupplierProfile', back_populates='supplier', uselist=False, lazy='select', cascade="all, delete-orphan")
    wallet = db.relationship('SupplierWallet', back_populates='supplier', uselist=False, lazy='select', cascade="all, delete-orphan")
    
    # العلاقة مع الطلبات (Orders)
    orders = db.relationship('Order', back_populates='supplier', lazy='select', cascade="all, delete-orphan")
    
    financials = db.relationship('OrderFinancial', back_populates='supplier', lazy='select', cascade="all, delete-orphan")
    
    # الربط مع الموظفين
    staff_members = db.relationship('SupplierStaff', back_populates='supplier', lazy='select', cascade="all, delete-orphan")
    
    # الربط مع منتجات قمرة (ProductSupplierMapping)
    product_mappings = db.relationship('ProductSupplierMapping', back_populates='supplier', lazy='dynamic')

    def __init__(self, **kwargs):
        """مُنشئ الكائن مع التشفير التلقائي لرقم الهاتف وتحديث حقل البحث السريع عند الإنشاء."""
        phone_val = kwargs.pop('phone', None)
        super().__init__(**kwargs)

        if phone_val is not None:
            self.phone = phone_val
        elif not self._phone_enc:
            self._phone_enc = self._encrypt("")

    # --- نظام التشفير السيادي ---
    @staticmethod
    def _get_key():
        key = os.environ.get('ENCRYPTION_KEY')
        return key.encode() if key else b'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8Vq='

    def _encrypt(self, value):
        if not value:
            return ""
        f = Fernet(self._get_key())
        return f.encrypt(str(value).encode()).decode()

    def _decrypt(self, value):
        if not value:
            return None
        try:
            f = Fernet(self._get_key())
            return f.decrypt(value.encode()).decode()
        except Exception:
            return None

    # --- Properties الذكية للتعامل مع رقم الهاتف ---
    @property
    def phone(self):
        return self._decrypt(self._phone_enc)

    @phone.setter
    def phone(self, value):
        if value:
            str_val = str(value)
            self._phone_enc = self._encrypt(str_val)
            self.search_phone = str_val[-9:]
        else:
            self._phone_enc = self._encrypt("")
            self.search_phone = None

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """تحويل المورد إلى قاموس آمن للاستخدام في APIs"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'supplier_code': self.supplier_code,
            'owner_name': self.owner_name,
            'trade_name': self.trade_name,
            'store_name': self.store_name,
            'phone': self.phone,
            'status': self.status,
            'rank': self.rank,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

    def __repr__(self):
        return f"<Supplier {self.id}: {self.store_name or self.trade_name or self.username}>"


# --- المحرك التلقائي لضبط الأكواد النمطية المتطابقة (SUP-963X و WEL-963X) ---
@event.listens_for(Supplier, 'after_insert')
def receive_after_insert(mapper, connection, target):
    """توليد الكود البصري للمورد (SUP-963X) وتحديث محفظته المقابلة بنفس الرقم (WEL-963X) تلقائياً."""
    from apps.models.wallet_db import SupplierWallet
    
    new_supplier_code = f"SUP-963{target.id}"
    new_wallet_code = f"WEL-963{target.id}"
    
    connection.execute(
        update(Supplier).where(Supplier.id == target.id).values(supplier_code=new_supplier_code)
    )
    
    connection.execute(
        update(SupplierWallet).where(SupplierWallet.supplier_id == target.id).values(wallet_code=new_wallet_code)
    )
