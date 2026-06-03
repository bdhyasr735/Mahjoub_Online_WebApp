# coding: utf-8
# 📂 apps/models/admin_db.py
# 🛡️ نظام إدارة هوية المالك المحصن - محجوب أونلاين 2026

from apps.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

class AdminUser(db.Model, UserMixin):
    """
    جدول المستخدم الإداري: يحتوي على بيانات الدخول الأساسية 
    مع دعم التحقق الثنائي (2FA) ونظام القفل التصاعدي ضد الاختراق.
    """
    __tablename__ = 'admin_users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    role = db.Column(db.String(50), default='admin')
    is_active = db.Column(db.Boolean, default=True)
    
    # 🔒 حقول الحماية الأمنية المضافة
    failed_attempts = db.Column(db.Integer, default=0)
    lock_until = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        """تشفير كلمة المرور قبل التخزين"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """التحقق من صحة كلمة المرور المدخلة"""
        return check_password_hash(self.password_hash, password)

    # 🛡️ منطق الحماية التصاعدية
    def is_locked(self):
        """التحقق من حالة القفل في السيرفر (Server-Side Lockdown)"""
        if self.lock_until and datetime.utcnow() < self.lock_until:
            return True
        return False

    def increment_failed_attempts(self):
        """زيادة عداد الفشل وتمديد وقت القفل"""
        self.failed_attempts += 1
        # زيادة المدة تدريجياً: (1, 2, 3...) دقيقة حسب عدد المحاولات الفاشلة
        delay = (self.failed_attempts // 10) + 1
        self.lock_until = datetime.utcnow() + timedelta(minutes=delay)
        db.session.commit()

    def reset_failed_attempts(self):
        """إعادة تعيين العداد عند النجاح"""
        self.failed_attempts = 0
        self.lock_until = None
        db.session.commit()

    def verify_otp_code(self, otp):
        """
        منطق التحقق من الـ OTP
        ملاحظة: هذا الكود يجب ربطه بخدمة واتساب السيادية 
        أو قاعدة بيانات مؤقتة لتخزين الكود المرسل
        """
        # هنا يجب كتابة منطق التحقق الخاص بك (مثلاً مقارنة بالـ Redis أو Database)
        return True # كمثال أولي للربط

    def __repr__(self):
        return f'<AdminUser {self.username}>'
