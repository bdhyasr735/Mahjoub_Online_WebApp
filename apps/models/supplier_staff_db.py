# coding: utf-8
# 📂 apps/models/supplier_staff_db.py

import os
from datetime import datetime
from cryptography.fernet import Fernet
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from apps.extensions import db


class SupplierStaff(db.Model, UserMixin):
    """نموذج موظفي الموردين - يدعم التشفير والعلاقات"""
    __tablename__ = 'supplier_staff'

    # [فهرسة متقدمة]: لضمان سرعة الاستعلامات والبحث
    __table_args__ = (
        db.Index('idx_staff_supplier_id', 'supplier_id'),
        db.Index('idx_staff_username', 'username'),
        db.Index('idx_staff_email_enc', '_email_enc'),
        db.Index('idx_staff_phone_enc', '_phone_enc'),
        db.Index('idx_staff_role', 'role'),
        db.Index('idx_staff_status', 'status'),
        db.Index('idx_staff_created', 'created_at'),
        {'extend_existing': True}
    )

    # ============================================================
    # ✅ الأعمدة الأساسية
    # ============================================================

    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)

    # ✅ حقل غير مشفر (للسرعة والبحث)
    username = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.String(50), default='staff')  # admin, manager, staff, viewer
    status = db.Column(db.String(20), default='active')  # active, inactive, suspended
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    # ✅ الحقول المشفرة (جميع البيانات الحساسة)
    _full_name_enc = db.Column(db.String(255), nullable=True)
    _email_enc = db.Column(db.String(255), nullable=True)
    _phone_enc = db.Column(db.String(255), nullable=True)
    _position_enc = db.Column(db.String(255), nullable=True)  # المسمى الوظيفي
    _address_enc = db.Column(db.String(500), nullable=True)

    # ✅ كلمة المرور (غير مشفرة بـ Fernet، بل باستخدام werkzeug)
    password_hash = db.Column(db.String(255), nullable=True)

    # ============================================================
    # ✅ العلاقات
    # ============================================================

    supplier = db.relationship(
        'Supplier',
        back_populates='staff_members',
        lazy='joined'
    )

    # ============================================================
    # ✅ نظام التشفير السيادي (Fernet)
    # ============================================================

    @staticmethod
    def _get_key():
        key = os.environ.get('ENCRYPTION_KEY')
        return key.encode() if key else b'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8Vq='

    def _encrypt(self, value):
        if not value:
            return None
        try:
            return Fernet(self._get_key()).encrypt(str(value).encode()).decode()
        except:
            return None

    def _decrypt(self, value):
        if not value:
            return None
        try:
            return Fernet(self._get_key()).decrypt(value.encode()).decode()
        except:
            return None

    # ============================================================
    # ✅ Properties المشفرة (getter / setter)
    # ============================================================

    @property
    def full_name(self):
        return self._decrypt(self._full_name_enc)

    @full_name.setter
    def full_name(self, value):
        self._full_name_enc = self._encrypt(value)

    @property
    def email(self):
        return self._decrypt(self._email_enc)

    @email.setter
    def email(self, value):
        self._email_enc = self._encrypt(value)

    @property
    def phone(self):
        return self._decrypt(self._phone_enc)

    @phone.setter
    def phone(self, value):
        self._phone_enc = self._encrypt(value)

    @property
    def position(self):
        return self._decrypt(self._position_enc)

    @position.setter
    def position(self, value):
        self._position_enc = self._encrypt(value)

    @property
    def address(self):
        return self._decrypt(self._address_enc)

    @address.setter
    def address(self, value):
        self._address_enc = self._encrypt(value)

    # ============================================================
    # ✅ نظام كلمة المرور (باستخدام werkzeug)
    # ============================================================

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # ============================================================
    # ✅ دوال مساعدة
    # ============================================================

    def to_dict(self):
        """تحويل الموظف إلى قاموس آمن (بدون كشف البيانات المشفرة)"""
        return {
            'id': self.id,
            'supplier_id': self.supplier_id,
            'username': self.username,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'position': self.position,
            'role': self.role,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
        }

    def __repr__(self):
        return f'<SupplierStaff {self.id}: {self.username} | {self.role} | {self.status}>'
