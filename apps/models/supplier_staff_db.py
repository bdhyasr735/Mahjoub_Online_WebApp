# -*- coding: utf-8 -*-
# 📂 apps/models/supplier_staff_db.py

import os
import enum
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import event, update, inspect
from apps.extensions import db


class SupplierStaffRole(str, enum.Enum):
    """أدوار موظفي وملاك الموردين المعتمدة في النظام"""
    ADMIN = 'admin'
    MANAGER = 'manager'
    STAFF = 'staff'
    VIEWER = 'viewer'


class SupplierStaff(db.Model, UserMixin):
    """نموذج موظفي الموردين والملاك - يدعم التشفير الكامل والكود التنظيمي الديناميكي"""
    __tablename__ = 'supplier_staff'

    # [فهرسة متقدمة]: لضمان سرعة الاستعلامات والبحث
    __table_args__ = (
        db.Index('idx_staff_supplier_id', 'supplier_id'),
        db.Index('idx_staff_username', 'username'),
        db.Index('idx_staff_code', 'staff_code'),
        db.Index('idx_staff_phone_search', 'search_phone'),
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
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id', ondelete='CASCADE'), nullable=False)
    
    # ✅ الكود التنظيمي الديناميكي التلقائي (مثل SUP9631-ST1)
    staff_code = db.Column(db.String(50), unique=True, nullable=True)

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
    search_phone = db.Column(db.String(20), nullable=True) # ✅ لسرعة مطابقة أرقام الهواتف (آخر 9 أرقام بدقة)
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
    # ✅ Properties المشفرة (getter / setter) مع المعيار الموحد 9 أرقام للهاتف
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
        if value:
            str_val = str(value)
            digits_only = "".join(filter(str.isdigit, str_val))
            # اعتماد معيار استخراج آخر 9 أرقام حصراً لضمان دقة البحث وعدم التكرار لجميع الشبكات (77, 78, 73, 71, 70)
            clean_9 = digits_only[-9:] if len(digits_only) >= 9 else digits_only
            
            self._phone_enc = self._encrypt(str_val)
            self.search_phone = clean_9
        else:
            self._phone_enc = None
            self.search_phone = None

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
    # ✅ التوقيت الموحد الدقيق (+3)
    # ============================================================

    @property
    def formatted_time(self):
        """تنسيق تاريخ الإنشاء بدقة (الساعة، الدقيقة، الثانية) بتوقيت اليمن/مكة (+3)"""
        if self.created_at:
            local_time = self.created_at + timedelta(hours=3)
            return local_time.strftime('%Y-%m-%d | %I:%M:%S %p')
        return "-"

    @property
    def formatted_last_login(self):
        """تنسيق وقت آخر تسجيل دخول بدقة (الساعة، الدقيقة، الثانية) بتوقيت اليمن/مكة (+3)"""
        if self.last_login:
            local_time = self.last_login + timedelta(hours=3)
            return local_time.strftime('%Y-%m-%d | %I:%M:%S %p')
        return "لم يسجل دخول بعد"

    # ============================================================
    # ✅ نظام كلمة المرور (باستخدام werkzeug)
    # ============================================================

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    # ============================================================
    # ✅ دوال مساعدة
    # ============================================================

    def to_dict(self):
        """تحويل الموظف إلى قاموس آمن للاستخدام في واجهات النظام"""
        return {
            'id': self.id,
            'supplier_id': self.supplier_id,
            'staff_code': self.staff_code,
            'username': self.username,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'search_phone': self.search_phone,
            'position': self.position,
            'role': self.role,
            'status': self.status,
            'formatted_time': self.formatted_time,
            'formatted_last_login': self.formatted_last_login,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
        }

    def __repr__(self):
        return f'<SupplierStaff {self.staff_code or self.id}: {self.username} | Role: {self.role} | Status: {self.status}>'


# --- توليد الكود التنظيمي الفريد للموظف فور الحفظ ---
@event.listens_for(SupplierStaff, 'after_insert')
def receive_staff_after_insert(mapper, connection, target):
    """توليد كود تنظيمي فريد للموظف مرتبط برقم المالك أو المورد الأساسي فور الحفظ"""
    new_staff_code = f"SUP963{target.supplier_id}-ST{target.id}"
    connection.execute(
        update(SupplierStaff).where(SupplierStaff.id == target.id).values(staff_code=new_staff_code)
    )
