# coding: utf-8
import os
from apps.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from apps.utils.security import AESCipher

cipher = AESCipher(os.getenv('ENCRYPTION_KEY', 'your-32-byte-key-here-must-be-secure'))

class AdminUser(db.Model, UserMixin):
    __tablename__ = 'admin_users'
    id = db.Column(db.Integer, primary_key=True)
    
    # الربط المباشر باسم العمود في Postgres
    full_name_enc = db.Column('full_name', db.String(255), nullable=False)
    email_enc = db.Column('email', db.String(255), unique=True, nullable=False)
    
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='admin')
    last_login = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def full_name(self): return cipher.decrypt(self.full_name_enc)
    @full_name.setter
    def full_name(self, value): self.full_name_enc = cipher.encrypt(str(value))

    @property
    def email(self): return cipher.decrypt(self.email_enc)
    @email.setter
    def email(self, value): self.email_enc = cipher.encrypt(str(value))
