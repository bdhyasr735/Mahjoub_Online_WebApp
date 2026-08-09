# -*- coding: utf-8 -*-
# 📂 apps/models/supplier_staff_db.py

import os
from datetime import datetime
from cryptography.fernet import Fernet
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from apps.extensions import db

class SupplierStaff(db.Model, UserMixin):
    __tablename__ = 'supplier_staff'
    
    __table_args__ = (
        db.Index('idx_sup_staff_username', 'username'),
        db.Index('idx_sup_staff_phone', 'search_phone'),
        db.Index('idx_sup_staff_active', 'is_active'),
        db.Index('idx_unique_staff_in_supplier', 'supplier_id', 'username', unique=True),
        {'extend_existing': True}
    )
    
    # 1. الأعمدة الأساسية
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    name = db.Column(db.String(150), nullable=True) # الحقل للإسم الكامل
    username = db.Column(db.String(100), nullable=False)
    
    # الهاتف المشفر
    _phone_enc = db.Column(db.String(255), nullable=True) 
    search_phone = db.Column(db.String(20)) 
    
    email = db.Column(db.String(150), nullable=True)
    password_hash = db.Column(db.String(500), nullable=False)
    
    role = db.Column(db.String(50), default='worker')
    role_title = db.Column(db.String(100), default='موظف مورد') # الحقل للمسمى الوظيفي
    is_active = db.Column(db.Boolean, default=True)
    
    # الصلاحيات
    permissions = db.Column(db.JSON, default=dict)
    can_view_wallet = db.Column(db.Boolean, default=False)
    can_manage_orders = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 3. العلاقات
    supplier = db.relationship(
        'Supplier', 
        back_populates='staff_members',
        lazy='joined' 
    )

    # 4. التشفير
    @staticmethod
    def _get_key():
        return os.environ.get('ENCRYPTION_KEY', 'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8Vq=').encode()

    @property
    def phone(self):
        try:
            return Fernet(self._get_key()).decrypt(self._phone_enc.encode()).decode()
        except: 
            return None

    @phone.setter
    def phone(self, value):
        if value:
            self._phone_enc = Fernet(self._get_key()).encrypt(str(value).encode()).decode()
            self.search_phone = str(value)[-9:] 

    def set_password(self, password):
        self.password_hash = generate_password_hash(password.strip(), method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password.strip())

    def to_dict(self):
        """تحويل بيانات الموظف إلى قاموس (Dictionary) لتسهيل تمريرها لصفحات الواجهة والـ JavaScript"""
        return {
            'id': self.id,
            'supplier_id': self.supplier_id,
            'name': self.name,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'role_title': self.role_title,
            'is_active': self.is_active,
            'permissions': self.permissions or {},
            'can_view_wallet': self.can_view_wallet,
            'can_manage_orders': self.can_manage_orders,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<SupplierStaff {self.username} | Active: {self.is_active}>'
