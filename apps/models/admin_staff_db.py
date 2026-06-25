# coding: utf-8
# 📂 apps/models/admin_staff_db.py

from apps.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class AdminStaff(db.Model):
    __tablename__ = 'admin_staff'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, index=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # رتب الإدارة: super_admin, logist_manager, accountant
    role = db.Column(db.String(50), default='admin', index=True) 
    is_active = db.Column(db.Boolean, default=True, index=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<AdminStaff {self.username} - {self.role}>'
