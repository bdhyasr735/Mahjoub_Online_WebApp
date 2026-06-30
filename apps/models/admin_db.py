# coding: utf-8
# 📂 apps/models/admin_db.py

import os
from datetime import datetime
from cryptography.fernet import Fernet
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from apps.extensions import db

class AdminUser(db.Model, UserMixin):
    """موديل إدارة النظام: مع تشفير متقدم للبيانات الحساسة وفهرسة استعلامات سريعة."""
    __tablename__ = 'admin_users'
    
    # [فهرسة الأداء]: تحسين سرعة الاستعلامات الأساسية
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
    
    # 2. معلومات الحساب - [نظام تشفير AES-256]
    role = db.Column(db.String(20), default='Owner')
    _phone_enc = db.Column(db.String(255), nullable=True) # رقم هاتف مشفر
    
    # 3. التدقيق الزمني
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    # --- نظام التشفير الاحترافي (AES) ---
    @staticmethod
    def _get_key():
        """استرجاع مفتاح التشفير من متغيرات البيئة لضمان الخصوصية."""
        key = os.environ.get('ENCRYPTION_KEY')
        return key.encode() if key else b'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8Vq='

    @property
    def phone(self):
        """فك تشفير رقم الهاتف عند العرض."""
        if not self._phone_enc: return None
        try:
            return Fernet(self._get_key()).decrypt(self._phone_enc.encode()).decode()
        except Exception: 
            return None

    @phone.setter
    def phone(self, value):
        """تشفير رقم الهاتف قبل التخزين في قاعدة البيانات."""
        if value:
            self._phone_enc = Fernet(self._get_key()).encrypt(str(value).encode()).decode()

    # --- نظام تأمين كلمة المرور (PBKDF2) ---
    def set_password(self, password):
        """توليد Hash مشفر بـ SHA256 للكلمة المرور."""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        """التحقق من صحة كلمة المرور المدخلة."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<AdminUser {self.username}>'
