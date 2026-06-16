# coding: utf-8
# 📂 apps/models/admin_db.py - نظام الهوية المحصن

from apps.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
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
    
    failed_attempts = db.Column(db.Integer, default=0)
    lock_until = db.Column(db.DateTime, nullable=True)

    @property
    def phone_number(self):
        """فك تشفير رقم الهاتف ديناميكياً باستخدام المفتاح المركزي للمنصة"""
        if self._phone_number_enc:
            try:
                # جلب المفتاح الآمن من الـ Config مباشرة لمنع الاستيراد الدائري
                cipher = Fernet(current_app.config['ENCRYPTION_KEY'].encode())
                return cipher.decrypt(self._phone_number_enc.encode()).decode()
            except Exception:
                # حماية للطوارئ في بيئة الـ Sandbox في حال كان النص غير مشفر قديماً
                return self._phone_number_enc
        return None
    
    @phone_number.setter
    def phone_number(self, value):
        """تشفير رقم الهاتف بمعيار سيادي آمن قبل حفظه في قاعدة البيانات"""
        if value:
            cipher = Fernet(current_app.config['ENCRYPTION_KEY'].encode())
            self._phone_number_enc = cipher.encrypt(str(value).encode()).decode()
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
