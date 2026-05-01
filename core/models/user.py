from core import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    """
    موديل المستخدمين - النواة السيادية للهوية الرقمية لمنصة محجوب أونلاين.
    يدعم تسجيل الدخول بالأسماء المركبة بالعربي مثل (علي محجوب).
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # المعرف الأساسي للدخول (يدعم الأسماء المركبة بالعربية)
    username = db.Column(db.String(150), unique=True, nullable=False)
    
    # البريد الإلكتروني (تم ضبطه ليكون اختيارياً لتفادي أي تعارض في البيانات)
    email = db.Column(db.String(120), unique=True, nullable=True)
    
    # حقل التشفير الأساسي (يجب أن يظل بهذا الاسم ليتطابق مع استعلامات SQL التلقائية)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # الرتبة الوظيفية: admin للقائد، supplier للموردين
    role = db.Column(db.String(20), nullable=False, default='supplier')
    
    # حالة الحساب (نشط/معلق) لضمان سيادة التحكم
    is_active_account = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def is_admin(self):
        """تحقق سريع لصلاحيات الإدارة المركزية (علي محجوب)"""
        return self.role == 'admin'

    def set_password(self, password):
        """تشفير كلمة المرور وتحويلها إلى رمز 'هاش' غير قابل للاختراق"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """مطابقة مفتاح التشفير المدخل مع المخزن في الترسانة الرقمية"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username} - Role: {self.role}>'
