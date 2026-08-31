# -*- coding: utf-8 -*-
# 📂 apps/models/admin_staff_db.py

import os
from datetime import datetime
from cryptography.fernet import Fernet
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from apps.extensions import db

class AdminStaff(db.Model, UserMixin):
    """موديل موظفي الإدارة: مع تشفير سيادي وفهرسة أداء متقدمة."""
    __tablename__ = 'admin_staff'
    
    __table_args__ = (
        db.Index('idx_admin_staff_username', 'username'),
        db.Index('idx_admin_staff_phone', 'search_phone'),
        db.Index('idx_admin_staff_created', 'created_at'),
        {'extend_existing': True}
    )
    
    # 1. الحقول الأساسية
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True) # الحقل المفقود للإسم الكامل
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True) # الحقل المفقود للبريد
    
    password_hash = db.Column(db.String(500), nullable=False)
    
    role = db.Column(db.String(20), default='worker')
    role_title = db.Column(db.String(100), default='موظف إدارة') # الحقل المفقود للمسمى الوظيفي
    is_active = db.Column(db.Boolean, default=True)
    
    # الصلاحيات الديناميكية الشاملة
    permissions = db.Column(db.JSON, default=dict)
    
    # 2. التشفير السيادي للهاتف
    _phone_enc = db.Column(db.String(255), nullable=True)
    search_phone = db.Column(db.String(20))
    
    # 3. التدقيق الزمني
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # --- نظام التشفير الاحترافي (Fernet / AES-256) ---
    @staticmethod
    def _get_key():
        return os.environ.get('ENCRYPTION_KEY', 'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8Vq=').encode()

    @property
    def phone(self):
        if not _phone_enc := self._phone_enc: 
            return None
        try:
            return Fernet(self._get_key()).decrypt(_phone_enc.encode()).decode()
        except Exception: 
            return None

    @phone.setter
    def phone(self, value):
        if value:
            self._phone_enc = Fernet(self._get_key()).encrypt(str(value).encode()).decode()
            self.search_phone = str(value)[-9:] 

    def set_password(self, password):
        self.password_hash = generate_password_hash(password.strip(), method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password.strip())

    def __repr__(self):
        return f'<AdminStaff {self.username}>'
