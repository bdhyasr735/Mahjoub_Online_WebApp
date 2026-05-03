from core import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import InternalError, ProgrammingError

class User(db.Model, UserMixin):
    # تحديد اسم الجدول ليتطابق مع النظام السيادي لـ "محجوب أونلاين"
    __tablename__ = 'users' 

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # الأعمدة الهيكلية (قد تكون مفقودة في قاعدة البيانات الحالية)
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

    @property
    def is_active(self):
        """صمام أمان: التحقق من نشاط الحساب مع حماية الجلسة"""
        try:
            # محاولة الوصول للعمود الحقيقي
            return self.is_active_account
        except (InternalError, ProgrammingError, Exception):
            # في حال وجود خطأ Transaction Aborted، نقوم بتطهير الجلسة فوراً
            db.session.rollback()
            return True # العودة للحالة الافتراضية لضمان استمرار النظام

    def __repr__(self):
        try:
            return f"<User {self.username} - Role: {self.role}>"
        except:
            db.session.rollback()
            return f"<User {self.username}>"

    # إضافة دوال Flask-Login الأساسية كاحتياط
    def get_id(self):
        return str(self.id)
