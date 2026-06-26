# coding: utf-8
# 📂 apps/models/admin_db.py

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from apps.extensions import db

class AdminUser(db.Model, UserMixin):
    __tablename__ = 'admin_user'
    
    # [صمام الأمان]: فهرسة مسمّاة ومنع تكرار التعريف
    __table_args__ = (
        db.Index('idx_adm_username', 'username'),
        db.Index('idx_adm_role', 'role'),
        db.Index('idx_adm_phone', 'phone_number'),
        {'extend_existing': True}
    )
    
    # 1. الحقول الأساسية
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # 2. معلومات الحساب
    role = db.Column(db.String(20), default='Owner')
    phone_number = db.Column(db.String(20))
    
    # 3. التدقيق الزمني
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    # [التشفير السيادي]: ترقية لـ PBKDF2:SHA256
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<AdminUser {self.username}>'
