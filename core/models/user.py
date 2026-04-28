from core import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    
    # تم رفع القيمة إلى 256 لإنهاء مشكلة "Data too long" في Render
    password_hash = db.Column(db.String(256), nullable=False)
    
    # تحديد الرتبة (مدير، مورد، مستخدم)
    role = db.Column(db.String(20), default='user') 
    
    # تحديد حالة الحساب (مفعل، معلق)
    status = db.Column(db.String(20), default='pending') 

    def set_password(self, password):
        """تشفير كلمة السر وتخزينها"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """التحقق من كلمة السر المدخلة مقابل المشفرة"""
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def is_supplier(self):
        return self.role == 'supplier'

    def is_approved(self):
        return self.status == 'approved'
