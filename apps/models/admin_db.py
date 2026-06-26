# coding: utf-8
# 📂 apps/models/admin_db.py

import os
from datetime import datetime
from cryptography.fernet import Fernet
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from apps.extensions import db

class AdminUser(db.Model, UserMixin):
    __tablename__ = 'admin_users'
    
    # [صمام الأمان]: فهرسة الأعمدة الحقيقية فقط
    __table_args__ = (
        db.Index('idx_adm_username', 'username'),
        db.Index('idx_adm_role', 'role'),
        db.Index('idx_adm_created', 'created_at'),
        {'extend_existing': True}
    )
    
    # 1. الحقول الأساسية
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # 2. معلومات الحساب - [تشفير سيادي]
    role = db.Column(db.String(20), default='Owner')
    _phone_enc = db.Column(db.String(255), nullable=True) 
    
    # 3. التدقيق الزمني
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    # --- نظام التشفير (AES) للرقم ---
    @staticmethod
    def _get_key():
        return os.environ.get('ENCRYPTION_KEY', 'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8Vq=').encode()

    @property
    def phone(self):
        if not self._phone_enc: return None
        try:
            return Fernet(self._get_key()).decrypt(self._phone_enc.encode()).decode()
        except: return None

    @phone.setter
    def phone(self, value):
        if value:
            self._phone_enc = Fernet(self._get_key()).encrypt(str(value).encode()).decode()

    # --- نظام تأمين كلمة المرور ---
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<AdminUser {self.username}>'
