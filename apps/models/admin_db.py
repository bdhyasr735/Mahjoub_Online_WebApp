# coding: utf-8
# 📂 apps/models/admin_db.py
# 🛡️ نظام إدارة هوية المالك - محجوب أونلاين 2026

from apps.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class AdminUser(db.Model, UserMixin):
    __tablename__ = 'admin_users'
    
    # المعرف الفريد للمستخدم
    id = db.Column(db.Integer, primary_key=True)
    
    # اسم المستخدم (علي محجوب)
    username = db.Column(db.String(100), unique=True, nullable=False)
    
    # كلمة المرور المشفرة (لا تُخزن أبداً كنص صريح)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # رقم الهاتف المعتمد لعمليات الـ 2FA عبر الواتساب
    phone_number = db.Column(db.String(20), nullable=False)
    
    # صلاحيات النظام
    role = db.Column(db.String(50), default='admin')
    
    # حالة التفعيل (للتحكم في الوصول)
    is_active = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        """تشفير كلمة المرور قبل تخزينها في قاعدة البيانات"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """التحقق من كلمة المرور المدخلة مقابل الـ Hash المخزن"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<AdminUser {self.username}>'
