# coding: utf-8
# 📂 apps/models/marketers_db.py

import os
from datetime import datetime
from cryptography.fernet import Fernet
from apps.extensions import db

class Marketer(db.Model):
    __tablename__ = 'marketers'

    # [صمام الأمان]: فهرسة مسمّاة ومنع تكرار التعريف
    __table_args__ = (
        db.Index('idx_mkt_name', 'full_name'),
        db.Index('idx_mkt_phone', 'phone'),
        db.Index('idx_mkt_code', 'marketing_code'),
        db.Index('idx_mkt_active', 'is_active'),
        db.Index('idx_mkt_refs', 'total_referrals'),
        db.Index('idx_mkt_created', 'created_at'),
        {'extend_existing': True}
    )

    id = db.Column(db.Integer, primary_key=True)
    
    # 1. البيانات الأساسية
    full_name = db.Column(db.String(150), nullable=False)
    
    # [تشفير سيادي]: تشفير الهاتف بـ AES
    _phone_enc = db.Column(db.String(255), nullable=True) 
    
    # 2. كود التسويق
    marketing_code = db.Column(db.String(50), unique=True, nullable=False)
    
    # 3. الحالة والإحصائيات
    is_active = db.Column(db.Boolean, default=True)
    total_referrals = db.Column(db.Integer, default=0)
    
    # 4. التوثيق
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # --- نظام التشفير (AES) ---
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

    def __repr__(self):
        return f'<Marketer {self.full_name} | Code: {self.marketing_code}>'
