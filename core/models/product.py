from core import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    """
    موديل المستخدمين المعدل ليتوافق مع قيود قاعدة البيانات الحالية.
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    
    # أضفنا هذا الحقل لأن قاعدة البيانات تطلبه إجبارياً (NotNullViolation)
    password = db.Column(db.String(255), nullable=True) 
    
    # الحقل الذي نستخدمه في الكود
    password_hash = db.Column(db.String(255), nullable=False)
    
    role = db.Column(db.String(20), nullable=False, default='supplier')
    is_active_account = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def is_admin(self):
        return self.role == 'admin'

    def set_password(self, password):
        # نقوم بتخزين الهاش في الحقلين لضمان تجاوز قيود قاعدة البيانات
        hashed = generate_password_hash(password)
        self.password_hash = hashed
        self.password = hashed # ليرضي قاعدة البيانات في العمود القديم

    def check_password(self, password):
        # التحقق من الهاش الرئيسي
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'
