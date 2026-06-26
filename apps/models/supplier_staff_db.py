# coding: utf-8
# 📂 apps/models/supplier_staff_db.py

from apps.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import UserMixin # ضروري جداً لـ Flask-Login

class SupplierStaff(db.Model, UserMixin): # إضافة UserMixin هنا
    __tablename__ = 'supplier_staff'
    
    # [صمام الأمان]: دمج الاندكسات في مكان واحد لمنع التكرار
    __table_args__ = (
        db.Index('idx_staff_supplier_id', 'supplier_id'),
        db.Index('idx_staff_username', 'username'),
        db.Index('idx_staff_email', 'email'),
        db.Index('idx_staff_role', 'role'),
        db.Index('idx_staff_active', 'is_active'),
        {'extend_existing': True}
    )

    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='worker')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # [العلاقات]: تحديد المسار لضمان عدم حدوث تداخل
    supplier = db.relationship(
        'Supplier', # تأكد أن الموديل مستورد بشكل صحيح في ملف الـ __init__ أو هنا
        back_populates='staff_members'
    )

    # [التشفير السيادي]: إعداد التشفير
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # [تعديل Flask-Login]: التأكد من أن المستخدم نشط
    def is_active(self):
        return self.is_active

    def __repr__(self):
        return f'<Staff {self.username} | Role: {self.role}>'
