# coding: utf-8
from apps import db
from cryptography.fernet import Fernet
import os
from datetime import datetime

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    
    # 1. المعرفات الأساسية
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    supplier_code = db.Column(db.String(50), unique=True, nullable=False, index=True) # MAH-VEN963
    
    # 2. البيانات الحساسة (تشفير AES)
    _phone_enc = db.Column(db.String(255), nullable=False) # الهاتف المشفر
    search_phone = db.Column(db.String(20), index=True)    # للفهرسة (بدون تشفير للسرعة)
    
    # 3. الحالات والرتب (لإدارة العمليات)
    status = db.Column(db.String(20), default='active', index=True) # active, pending, suspended
    rank = db.Column(db.String(20), default='bronze', index=True)   # bronze, silver, gold
    
    # 4. التدقيق الزمني (Audit)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    last_login = db.Column(db.DateTime, nullable=True)

    # 5. العلاقة مع الملف الشخصي (الربط المفقود)
    supplier_profile = db.relationship(
        'SupplierProfile', 
        back_populates='supplier', 
        uselist=False,
        cascade="all, delete-orphan"
    )

    # --- نظام التشفير السيادي ---
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
        self.search_phone = str(value)[:20] # للفهرسة السريعة

    def __repr__(self):
        return f'<Supplier {self.username}>'
