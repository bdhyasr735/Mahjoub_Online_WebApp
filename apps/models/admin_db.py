# coding: utf-8
# 📂 apps/models/admin_db.py - نظام الهوية المحصن (نسخة نهائية)

from apps.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from apps.utils.security import AESCipher 

class AdminUser(db.Model, UserMixin):
    __tablename__ = 'admin_users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # حقل الهاتف مشفر - nullable=True ضروري لتجنب NotNullViolation
    _phone_number_enc = db.Column(db.String(255), nullable=True)
    
    role = db.Column(db.String(50), default='admin')
    is_active = db.Column(db.Boolean, default=True)
    
    failed_attempts = db.Column(db.Integer, default=0)
    lock_until = db.Column(db.DateTime, nullable=True)

    @property
    def phone_number(self): 
        if self._phone_number_enc:
            return AESCipher.decrypt(self._phone_number_enc)
        return None
    
    @phone_number.setter
    def phone_number(self, value): 
        if value:
            self._phone_number_enc = AESCipher.encrypt(str(value))
        else:
            self._phone_number_enc = None

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def is_locked(self):
        if self.lock_until and datetime.utcnow() < self.lock_until:
            return True
        return False

    def increment_failed_attempts(self):
        self.failed_attempts = (self.failed_attempts or 0) + 1
        delay = (self.failed_attempts // 5) + 1 
        self.lock_until = datetime.utcnow() + timedelta(minutes=delay)

    def reset_failed_attempts(self):
        self.failed_attempts = 0
        self.lock_until = None

    def __repr__(self):
        return f'<AdminUser {self.username}>'
