from core import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    # تحديد اسم الجدول ليتطابق مع مفتاح الربط في النظام السيادي لـ "محجوب أونلاين"
    __tablename__ = 'users' 

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # هذه الأعمدة هي المسببة للخطأ حالياً لأنها غير موجودة في قاعدة البيانات الواقعية
    role = db.Column(db.String(50), default='admin') 
    is_active_account = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        """تشفير كلمة المرور قبل الحفظ"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """التحقق من صحة كلمة المرور"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    # تحسين خصائص Flask-Login لضمان استقرار الجلسة
    @property
    def is_active(self):
        # في حال فقدان العمود، سيعتبر الحساب نشطاً تلقائياً لمنع قفل النظام
        return getattr(self, 'is_active_account', True)

    def __repr__(self):
        return f"<User {self.username} - Role: {getattr(self, 'role', 'N/A')}>"
