from core import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    """
    موديل المستخدمين - التركيز الكامل على 'اسم المستخدم' كمعرف سيادي.
    تم ضبط الحقول الأخرى لتكون مرنة لمنع انهيار السيرفر بسبب نقص الأعمدة.
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # اسم المستخدم: المعرف الأساسي والوحيد المطلوب للدخول (يدعم العربية)
    username = db.Column(db.String(150), unique=True, nullable=False)
    
    # البريد الإلكتروني: اختياري (Nullable) لحل مشكلة UndefinedColumn في الجداول القديمة
    email = db.Column(db.String(120), unique=True, nullable=True)
    
    # مفتاح التشفير لكلمة المرور
    password_hash = db.Column(db.String(255), nullable=False)
    
    # حوكمة الأدوار: (admin للقيادة، supplier للموردين)
    role = db.Column(db.String(20), nullable=False, default='supplier')
    
    # الحالة التشغيلية للحساب: تفعيل أو إيقاف بقرار من القائد
    is_active_account = db.Column(db.Boolean, default=True)
    
    # تاريخ الانضمام للمنصة
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def is_admin(self):
        """التحقق السريع من صلاحيات الإدارة"""
        return self.role == 'admin'

    def set_password(self, password):
        """توليد الهاش المشفر لضمان أمان الترسانة الرقمية"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """المقارنة الذكية عند تسجيل الدخول"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username} - Role: {self.role}>'
