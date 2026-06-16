# coding: utf-8
# 📂 apps/models/admin_db.py

import os
from apps.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
from flask import current_app

class AdminUser(db.Model, UserMixin):
    __tablename__ = 'admin_users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    _phone_number_enc = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(50), default='admin')
    is_active = db.Column(db.Boolean, default=True)

    def _get_encryption_key(self):
        # الاعتماد على الإعدادات المركزية
        return current_app.config.get('ENCRYPTION_KEY') or os.environ.get('ENCRYPTION_KEY')

    @property
    def phone_number(self):
        if self._phone_number_enc:
            try:
                key = self._get_encryption_key()
                if key:
                    cipher = Fernet(key.encode())
                    return cipher.decrypt(self._phone_number_enc.encode()).decode()
            except:
                return "Error"
        return ""
    
    @phone_number.setter
    def phone_number(self, value):
        if value:
            key = self._get_encryption_key()
            if key:
                cipher = Fernet(key.encode())
                self._phone_number_enc = cipher.encrypt(str(value).encode()).decode()
            else:
                self._phone_number_enc = str(value)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
