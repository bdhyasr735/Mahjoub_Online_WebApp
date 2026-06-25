# coding: utf-8
# 📂 apps/models/supplier_db.py

from apps.extensions import db
from cryptography.fernet import Fernet
import os
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Supplier(db.Model, UserMixin):
    __tablename__ = 'suppliers'
    
    # 1. المعرفات الأساسية
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    
    supplier_code = db.Column(db.String(50), unique=True, nullable=True, index=True) 
    trade_name = db.Column(db.String(150), nullable=True)
    
    # 2. البيانات الحساسة (تشفير AES)
    _phone_enc = db.Column(db.String(255), nullable=False) 
    search_phone = db.Column(db.String(20), index=True)
    
    # 3. بيانات المصادقة
    password_hash = db.Column(db.String(255), nullable=True)
    
    # 4. الحالات والرتب
    status = db.Column(db.String(20), default='active', index=True)
    rank = db.Column(db.String(20), default='bronze', index=True)
    
    # 5. التدقيق الزمني
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    last_login = db.Column(db.DateTime, nullable=True)

    # 6. العلاقات
    supplier_profile = db.relationship(
        'SupplierProfile', 
        back_populates='supplier', 
        uselist=False,
        cascade="all, delete-orphan"
    )
    
    wallet = db.relationship('SupplierWallet', back_populates='supplier', uselist=False, cascade="all, delete-orphan")
    
    orders = db.relationship('Order', back_populates='supplier', cascade="all, delete-orphan")
    financials = db.relationship('OrderFinancial', back_populates='supplier', cascade="all, delete-orphan")

    # --- منطق توليد الأكواد التلقائي ---
    def generate_codes(self):
        """توليد كود المورد والمحفظة تلقائياً"""
        if self.id and not self.supplier_code:
            self.supplier_code = f"MAH-SUP963{self.id}"
            
            from apps.models.wallet_db import SupplierWallet
            # التعديل هنا: استخدام أسماء الأعمدة الصحيحة (balance_available / balance_pending)
            new_wallet = SupplierWallet(
                wallet_code=f"MAH-WEL963{self.id}",
                supplier_id=self.id,
                balance_available=0.00,
                balance_pending=0.00
            )
            db.session.add(new_wallet)

    # --- نظام التشفير للرقم (AES) ---
    @staticmethod
    def _get_key():
        return os.environ.get('ENCRYPTION_KEY', 'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8Vq=').encode()

    @property
    def phone(self):
        try:
            return Fernet(self._get_key()).decrypt(self._phone_enc.encode()).decode()
        except:
            return None

    @phone.setter
    def phone(self, value):
        self._phone_enc = Fernet(self._get_key()).encrypt(str(value).encode()).decode()
        self.search_phone = str(value)[:20]

    # --- نظام المصادقة بكلمة المرور ---
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Supplier {self.username}>'
