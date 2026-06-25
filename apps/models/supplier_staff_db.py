# coding: utf-8
# 📂 apps/models/supplier_staff_db.py

from apps.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class SupplierStaff(db.Model):
    __tablename__ = 'supplier_staff'
    
    # حل جذري لتجنب خطأ التكرار في تعريف الجدول عند إعادة التحميل
    __table_args__ = {'extend_existing': True}

    # 1. المعرفات
    id = db.Column(db.Integer, primary_key=True)
    
    # 2. الربط مع المورد (مع Index للبحث السريع)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False, index=True)
    
    # 3. بيانات الموظف (مع Index للبحث)
    username = db.Column(db.String(100), nullable=False, index=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # 4. الصلاحيات والحالة (مع Index للتصفية السريعة)
    role = db.Column(db.String(50), default='worker', index=True) # owner, processor, accountant
    is_active = db.Column(db.Boolean, default=True, index=True)
    
    # 5. التوثيق
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # 6. الربط العكسي
    supplier = db.relationship('Supplier', back_populates='staff_members')

    # --- دوال الأمان ---
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Staff {self.username} | Role: {self.role}>'
