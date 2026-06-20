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
    
    # --- حقول الهوية والمطابقة لجميع الحسابات ---
    username = db.Column(db.String(100), unique=True, nullable=False)        # اسم المستخدم المعتمد
    # تم إضافة القيمة الافتراضية لحساب المالك لتجنب قيود nullable=False أثناء تهيئة النظام تلقائياً
    admin_email = db.Column(db.String(150), unique=True, nullable=False, default='mahjoubpnline@outlook.sa')
    password_hash = db.Column(db.String(255), nullable=False)
    _phone_number_enc = db.Column(db.String(255), nullable=True)              # الهاتف الإداري المشفر بـ Fernet
    
    # --- فرز رتب السيادة والحوكمة ---
    role = db.Column(db.String(50), default='supplier') # (super_admin, admin, supplier, marketer)
    
    # --- فهارس البحث السريع وعابر الأنظمة ---
    admin_code = db.Column(db.String(100), unique=True, nullable=True)       # الكود السيادي المتولد آلياً
    search_name = db.Column(db.String(150), index=True, nullable=True)
    search_phone = db.Column(db.String(20), index=True, nullable=True)
    
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 🔗 الربط الموحد: التوجيه الصحيح إلى الكلاس الفعلي المسؤول عن البيانات التجارية 'SupplierProfile'
    supplier_profile = db.relationship('SupplierProfile', back_populates='user', uselist=False, lazy='joined')

    # --- نظام توليد الأكواد الآلي الموحد ---
    def generate_sovereign_code(self):
        """توليد الأكواد بناءً على الرتبة المحددة للحساب"""
        if self.id and not self.admin_code:
            if self.role in ['super_admin', 'admin']:
                self.admin_code = f"ADMIN-MAH963{self.id}"
            elif self.role == 'supplier':
                self.admin_code = f"SUP-MAH963{self.id}"
            else:
                self.admin_code = f"USER-MAH963{self.id}"

    def _get_encryption_key(self):
        try:
            return current_app.config.get('ENCRYPTION_KEY') or os.environ.get('ENCRYPTION_KEY', 'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8Vq=')
        except:
            return os.environ.get('ENCRYPTION_KEY', 'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8Vq=')

    @property
    def phone_number(self):
        if self._phone_number_enc:
            try:
                key = self._get_encryption_key()
                cipher = Fernet(key.encode())
                return cipher.decrypt(self._phone_number_enc.encode()).decode()
            except:
                return "Error"
        return ""
    
    @phone_number.setter
    def phone_number(self, value):
        if value:
            key = self._get_encryption_key()
            cipher = Fernet(key.encode())
            self._phone_number_enc = cipher.encrypt(str(value).encode()).decode()
            self.search_phone = str(value)[:20]
            if self.username:
                self.search_name = str(self.username)[:150]
        else:
            self._phone_number_enc = None

    def set_password(self, password): 
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password): 
        return check_password_hash(self.password_hash, password)

# 🔗 حقن موديول الكيان التجاري للمورد هنا في النهاية لكسر جمود الـ Mapper تماماً
from apps.models.supplier_profile_db import SupplierProfile
