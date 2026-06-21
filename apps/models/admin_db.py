# coding: utf-8
# 📂 apps/models/admin_db.py - نظام الهوية الموحد للمنصة (إدارة وموردين)

import os
from apps.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
from flask import current_app
from datetime import datetime

class AdminUser(db.Model, UserMixin):
    __tablename__ = 'admin_users'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # --- حقول الهوية والمطابقة ---
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    admin_email = db.Column(db.String(150), unique=True, nullable=False, default='mahjoubpnline@outlook.sa')
    password_hash = db.Column(db.String(255), nullable=False)
    
    # الهاتف مشفر بـ Fernet (آمن جداً)
    _phone_number_enc = db.Column(db.String(255), nullable=True)
    
    # --- فرز رتب السيادة ---
    role = db.Column(db.String(50), default='supplier', index=True) 
    
    # --- فهارس البحث السريع (تم التأكد منها للتحمل المليوني) ---
    admin_code = db.Column(db.String(100), unique=True, nullable=True, index=True)
    search_name = db.Column(db.String(150), index=True, nullable=True)
    search_phone = db.Column(db.String(20), index=True, nullable=True) # مفهرس للبحث السريع
    
    is_active = db.Column(db.Boolean, default=True, index=True)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # 🔗 الربط الموحد: التوجيه الصحيح إلى SupplierProfile
    supplier_profile = db.relationship('SupplierProfile', back_populates='user', uselist=False, lazy='joined')

    # --- نظام توليد الأكواد الآلي ---
    def generate_sovereign_code(self):
        if self.id and not self.admin_code:
            if self.role in ['super_admin', 'admin']:
                self.admin_code = f"ADMIN-MAH963{self.id}"
            elif self.role == 'supplier':
                self.admin_code = f"SUP-MAH963{self.id}"
            else:
                self.admin_code = f"USER-MAH963{self.id}"

    def _get_encryption_key(self):
        return os.environ.get('ENCRYPTION_KEY', 'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8Vq=')

    @property
    def phone_number(self):
        if self._phone_number_enc:
            try:
                key = self._get_encryption_key()
                cipher = Fernet(key.encode())
                return cipher.decrypt(self._phone_number_enc.encode()).decode()
            except:
                return None
        return ""
    
    @phone_number.setter
    def phone_number(self, value):
        if value:
            key = self._get_encryption_key()
            cipher = Fernet(key.encode())
            self._phone_number_enc = cipher.encrypt(str(value).encode()).decode()
            # التحديث الموازي للبحث السريع
            self.search_phone = str(value)[:20]
            self.search_name = str(self.username)[:150]
        else:
            self._phone_number_enc = None
            self.search_phone = None

    def set_password(self, password): 
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password): 
        return check_password_hash(self.password_hash, password)

# استيراد لاحق لكسر جمود الـ Mapper
from apps.models.supplier_profile_db import SupplierProfile
