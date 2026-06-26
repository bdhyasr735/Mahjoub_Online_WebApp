# coding: utf-8
# 📂 apps/models/admin_staff_db.py

from apps.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class AdminStaff(db.Model):
    __tablename__ = 'admin_staff'

    # استراتيجية الاندكس (Index) والشفر (Encryption)
    __table_args__ = (
        db.Index('idx_admin_username', 'username'),
        db.Index('idx_admin_email', 'email'),
        db.Index('idx_admin_role', 'role'),
        db.Index('idx_admin_active', 'is_active'),
        {'extend_existing': True} # صمام الأمان لمنع فصل السيرفر
    )

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='admin')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # استراتيجية الشفر (Encryption): تشفير بمستوى pbkdf2
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<AdminStaff {self.username} - {self.role}>'
