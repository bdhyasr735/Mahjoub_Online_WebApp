from core import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    
    # تأكد من وجود هذين السطرين تحديداً
    role = db.Column(db.String(20), default='user') # 'admin' or 'supplier'
    status = db.Column(db.String(20), default='pending') # 'approved' or 'pending'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
