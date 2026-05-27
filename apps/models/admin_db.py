# coding: utf-8
# 🛡️ جدول إدارة النظام المشفر - منصة محجوب أونلاين 2026
import os
from apps.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from apps.utils.security import AESCipher

# تهيئة مشفر البيانات
cipher = AESCipher(os.getenv('ENCRYPTION_KEY', 'your-32-byte-key-here-must-be-secure'))

class AdminUser(db.Model, UserMixin):
    __tablename__ = 'admin_users'

    id = db.Column(db.Integer, primary_key=True)
    
    # الأعمدة في قاعدة البيانات (بدون شرطة سفلية)
    # ملاحظة: إذا كان اسم العمود في قاعدة البيانات حالياً هو '_full_name'، 
    # فيجب عليك تعديل اسم العمود في جدول Postgres عبر أمر SQL أو تغيير الكود أدناه لـ '_full_name'
    full_name_encrypted = db.Column('full_name', db.String(255), nullable=False)
    email_encrypted = db.Column('email', db.String(255), unique=True, nullable=False)
    
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    role = db.Column(db.String(50), default='admin')
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # --- خصائص التشفير ---

    @property
    def full_name(self): 
        return cipher.decrypt(self.full_name_encrypted)
    
    @full_name.setter
    def full_name(self, value): 
        self.full_name_encrypted = cipher.encrypt(str(value))

    @property
    def email(self): 
        return cipher.decrypt(self.email_encrypted)
    
    @email.setter
    def email(self, value): 
        self.email_encrypted = cipher.encrypt(str(value))

    # --- طرق الأمان ---

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<AdminUser {self.username}>'
