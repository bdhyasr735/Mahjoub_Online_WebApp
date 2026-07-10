# coding: utf-8
# 📂 apps/models/supplier_staff_db.py

import os
from datetime import datetime
from cryptography.fernet import Fernet
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from apps.extensions import db

class SupplierStaff(db.Model, UserMixin):
    __tablename__ = 'supplier_staff'
    
    # [فهرسة متقدمة]: فهرسة الحقول الأكثر استخداماً في البحث والفلترة
    __table_args__ = (
        db.Index('idx_sup_staff_username', 'username'),
        db.Index('idx_sup_staff_phone', 'search_phone'),
        db.Index('idx_sup_staff_active', 'is_active'),
        # فهرس فريد مركب لمنع تكرار الموظف لنفس المورد
        db.Index('idx_unique_staff_in_supplier', 'supplier_id', 'username', unique=True),
        {'extend_existing': True}
    )
    
    # 1. الأعمدة
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    
    # [التشفير السيادي]: الهاتف مشفر وله فهرس للبحث
    _phone_enc = db.Column(db.String(255), nullable=False) 
    search_phone = db.Column(db.String(20)) 
    
    email = db.Column(db.String(150), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='worker')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 3. العلاقات: استخدمنا lazy='joined' لأن الموظف يحتاج دائماً لبيانات المورد التابع له
    # هذا يقلل عدد الاستعلامات ويحسن أداء لوحة التحكم بشكل ملحوظ
    supplier = db.relationship(
        'Supplier', 
        back_populates='staff_members',
        lazy='joined' 
    )

    # 4. التشفير (Fernet AES-256)
    @staticmethod
    def _get_key():
        return os.environ.get('ENCRYPTION_KEY', 'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8Vq=').encode()

    @property
    def phone(self):
        """فك تشفير الهاتف عند الاستدعاء"""
        try:
            return Fernet(self._get_key()).decrypt(self._phone_enc.encode()).decode()
        except: 
            return None

    @phone.setter
    def phone(self, value):
        """تشفير الهاتف وتحديث فهرس البحث"""
        if value:
            self._phone_enc = Fernet(self._get_key()).encrypt(str(value).encode()).decode()
            self.search_phone = str(value)[-9:] 

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<SupplierStaff {self.username} | Role: {self.role}>'
