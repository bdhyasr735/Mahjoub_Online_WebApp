# coding: utf-8
# 📂 apps/models/supplier_db.py - الكيان السيادي لبيانات الموردين (مفهرس بالكامل)

from apps.extensions import db
from flask_login import UserMixin
from datetime import datetime
from apps.utils.security import AESCipher

class Supplier(db.Model, UserMixin):
    """
    الجدول الأساسي والمحكم لإدارة كيانات الموردين.
    تم إضافة فهارس (Indexes) لجميع حقول البحث لضمان سرعة الاستجابة مع ملايين السجلات.
    """
    __tablename__ = 'suppliers'

    # المفتاح الأساسي مفهرس تلقائياً بواسطة SQLAlchemy
    id = db.Column(db.Integer, primary_key=True)
    
    # 🔗 الجسر السيادي (مفهرس لأنه حقل ربط)
    admin_user_id = db.Column(db.Integer, db.ForeignKey('admin_users.id'), unique=True, nullable=True, index=True)

    # حقول البحث الأساسية (مفهرسة لسرعة الاستعلام)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    trade_name = db.Column(db.String(150), nullable=False, index=True) # مفهرس للبحث بالاسم
    status = db.Column(db.String(20), default='active', nullable=False, index=True) # مفهرس لتصفية الحسابات النشطة
    
    # حقول مشفرة
    _owner_phone = db.Column('owner_phone', db.String(255), nullable=True)
    
    # ⚡ حقل الفهرسة (البحث السريع للرقم)
    phone_index = db.Column(db.String(50), index=True, nullable=True) 
    
    _country_code = db.Column('country_code', db.String(10), nullable=True)
    _owner_email = db.Column('owner_email', db.String(255), nullable=True, index=True) # مفهرس للبحث بالإيميل
    
    # الأكواد السيادية (مفهرس لأنه معرف فريد للبحث)
    supplier_code = db.Column(db.String(50), unique=True, nullable=True, index=True)
    
    # مفهرس للتقارير الزمنية (أحدث الموردين)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # 🔗 العلاقات البرمجية
    wallet = db.relationship('SupplierWallet', back_populates='supplier', uselist=False, lazy=True, cascade="all, delete-orphan")

    # --- Property للتحكم في الهاتف ---
    @property
    def full_phone(self):
        phone = self.owner_phone
        return f"{self._country_code}{phone}" if self._country_code and phone else None

    @property
    def owner_phone(self):
        try:
            return AESCipher.decrypt(self._owner_phone) if self._owner_phone else None
        except Exception:
            return None

    @owner_phone.setter
    def owner_phone(self, value):
        if value:
            clean_phone = "".join(value.split())
            self._owner_phone = AESCipher.encrypt(clean_phone)
            self.phone_index = clean_phone 
        else:
            self._owner_phone = None
            self.phone_index = None

    # --- Property للتحكم في البريد الإلكتروني ---
    @property
    def owner_email(self):
        try:
            return AESCipher.decrypt(self._owner_email) if self._owner_email else None
        except Exception:
            return None

    @owner_email.setter
    def owner_email(self, value):
        if value:
            self._owner_email = AESCipher.encrypt(value)
        else:
            self._owner_email = None

    def generate_codes(self):
        if not self.supplier_code and self.id:
            self.supplier_code = f"SUP-MAH{self.id}x{datetime.utcnow().strftime('%y%m')}"
            
    def __repr__(self):
        return f"<Supplier [{self.supplier_code}] -> {self.trade_name}>"
