from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# تعريف قاعدة البيانات
db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    # حقل اسم المستخدم يدعم العربية وبحد أقصى 150 حرفاً
    username = db.Column(db.String(150), unique=True, nullable=False)
    # حقل كلمة المرور المشفرة
    password = db.Column(db.String(255), nullable=False)
    # رتبة المستخدم (أدمن، مورد، إلخ)
    role = db.Column(db.String(50), default='SuperAdmin')

    def set_password(self, password):
        """تحويل كلمة المرور العادية إلى بصمة مشفرة"""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """التحقق من كلمة المرور المدخلة مقارنة بالمشفرة"""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User {self.username}>'
