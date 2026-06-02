# coding: utf-8
import os
from apps.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
# تأكد من أن مسار الاستيراد هذا صحيح بناءً على هيكلية مشروعك
from apps.utils import AESCipher 

# تهيئة مشفر البيانات السيادي
encryption_key = os.getenv('ENCRYPTION_KEY', '00000000000000000000000000000000')
cipher = AESCipher(encryption_key)

class AdminUser(db.Model, UserMixin):
    __tablename__ = 'admin_users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='admin')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<AdminUser {self.username}>'
