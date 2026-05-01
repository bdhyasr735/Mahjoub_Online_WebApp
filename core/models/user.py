from core import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    """
    موديل المستخدمين - النواة السيادية للهوية الرقمية لمنصة محجوب أونلاين.
    تم تجريد الموديل من البريد الإلكتروني ليعتمد كلياً على اسم المستخدم بالعربي.
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # المعرف الأساسي والوحيد للدخول (مثل: علي محجوب)
    username = db.Column(db.String(150), unique=True, nullable=False)
    
    # حقل التشفير الأساسي لكلمة المرور
    password_hash = db.Column(db.String(255), nullable=False)
    
    # الرتبة الوظيفية: admin للقائد، supplier للموردين
    role = db.Column(db.String(20), nullable=False, default='supplier')
    
    # حالة الحساب (نشط/معلق) لضمان التحكم المركزي
    is_active_account = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def is_admin(self):
        """تحقق سريع لصلاحيات الإدارة المركزية"""
        return self.role == 'admin'

    def set_password(self, password):
        """تشفير كلمة المرور وتحويلها إلى رمز 'هاش' آمن"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """مطابقة مفتاح التشفير المدخل مع المخزن في القاعدة"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username} - Role: {self.role}>'
