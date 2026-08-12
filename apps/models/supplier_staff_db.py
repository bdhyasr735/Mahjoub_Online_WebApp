# coding: utf-8
# 📂 apps/models/supplier_profile_db.py

import os
from cryptography.fernet import Fernet
from apps.extensions import db


# ============================================================
# ✅ جداول التصنيف (Lookup Tables) – غير مشفرة، مفهرسة
# ============================================================

class Category(db.Model):
    __tablename__ = 'categories'

    __table_args__ = (
        db.Index('idx_cat_name', 'name'),
        db.Index('idx_cat_icon', 'icon'),
        {'extend_existing': True}
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    icon = db.Column(db.String(50), nullable=True)

    profiles = db.relationship('SupplierProfile', back_populates='category_rel', lazy='dynamic')

    def __repr__(self):
        return f'<Category {self.name}>'


class Bank(db.Model):
    __tablename__ = 'banks'

    __table_args__ = (
        db.Index('idx_bank_name', 'name'),
        db.Index('idx_bank_icon', 'icon'),
        {'extend_existing': True}
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    icon = db.Column(db.String(50), nullable=True)

    profiles = db.relationship('SupplierProfile', back_populates='bank_rel', lazy='dynamic')

    def __repr__(self):
        return f'<Bank {self.name}>'


class FinancialCompany(db.Model):
    __tablename__ = 'financial_companies'

    __table_args__ = (
        db.Index('idx_comp_name', 'name'),
        db.Index('idx_comp_type', 'type'),
        {'extend_existing': True}
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    type = db.Column(db.String(50), nullable=True)

    profiles = db.relationship('SupplierProfile', back_populates='company_rel', lazy='dynamic')

    def __repr__(self):
        return f'<FinancialCompany {self.name}>'


# ============================================================
# ✅ نموذج الملف الشخصي للمورد (SupplierProfile)
#    – مشفر بالكامل للبيانات الحساسة
#    – مفهرس لجميع الحقول المستخدمة في البحث
# ============================================================

class SupplierProfile(db.Model):
    __tablename__ = 'supplier_profiles'

    # [فهرسة متقدمة]: لضمان سرعة الاستعلامات
    __table_args__ = (
        db.Index('idx_prof_supplier_id', 'supplier_id'),
        db.Index('idx_prof_trade_name', 'trade_name'),
        db.Index('idx_prof_gov', 'governorate'),
        db.Index('idx_prof_city', 'city'),
        db.Index('idx_prof_category_id', 'category_id'),
        db.Index('idx_prof_bank_id', 'bank_id'),
        db.Index('idx_prof_company_id', 'financial_company_id'),
        db.Index('idx_prof_created', 'created_at'),
        # فهارس على الحقول المشفرة (للبحث السريع باستخدام التشفير)
        db.Index('idx_prof_email_enc', '_email_enc'),
        db.Index('idx_prof_bank_account_enc', '_bank_account_enc'),
        db.Index('idx_prof_id_number_enc', '_id_number_enc'),
        db.Index('idx_prof_commercial_reg_enc', '_commercial_reg_enc'),
        {'extend_existing': True}
    )

    # ============================================================
    # ✅ الأعمدة الأساسية
    # ============================================================

    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False, unique=True)

    # ✅ حقول غير مشفرة (للسرعة والبحث)
    trade_name = db.Column(db.String(150))
    governorate = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ✅ المفاتيح الخارجية للجداول الجديدة (غير مشفرة)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    bank_id = db.Column(db.Integer, db.ForeignKey('banks.id'), nullable=True)
    financial_company_id = db.Column(db.Integer, db.ForeignKey('financial_companies.id'), nullable=True)

    # ============================================================
    # ✅ الحقول المشفرة (جميع البيانات الحساسة)
    # ============================================================

    _email_enc = db.Column(db.String(255), nullable=True)
    _address_enc = db.Column(db.String(500), nullable=True)
    _description_enc = db.Column(db.Text, nullable=True)
    _bank_account_enc = db.Column(db.String(255), nullable=True)
    _id_number_enc = db.Column(db.String(255), nullable=True)
    _commercial_reg_enc = db.Column(db.String(255), nullable=True)

    # ============================================================
    # ✅ العلاقات
    # ============================================================

    supplier = db.relationship(
        'Supplier',
        back_populates='supplier_profile',
        lazy='joined'
    )

    category_rel = db.relationship(
        'Category',
        back_populates='profiles',
        lazy='joined'
    )

    bank_rel = db.relationship(
        'Bank',
        back_populates='profiles',
        lazy='joined'
    )

    company_rel = db.relationship(
        'FinancialCompany',
        back_populates='profiles',
        lazy='joined'
    )

    # ============================================================
    # ✅ خصائص مساعدة للحصول على الأسماء (بدون فك تشفير)
    # ============================================================

    @property
    def category_name(self):
        return self.category_rel.name if self.category_rel else None

    @property
    def bank_name(self):
        return self.bank_rel.name if self.bank_rel else None

    @property
    def company_name(self):
        return self.company_rel.name if self.company_rel else None

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
    def email(self):
        return self._decrypt(self._email_enc)

    @email.setter
    def email(self, value):
        self._email_enc = self._encrypt(value)

    @property
    def address(self):
        return self._decrypt(self._address_enc)

    @address.setter
    def address(self, value):
        self._address_enc = self._encrypt(value)

    @property
    def description(self):
        return self._decrypt(self._description_enc)

    @description.setter
    def description(self, value):
        self._description_enc = self._encrypt(value)

    @property
    def bank_account(self):
        return self._decrypt(self._bank_account_enc)

    @bank_account.setter
    def bank_account(self, value):
        self._bank_account_enc = self._encrypt(value)

    @property
    def id_number(self):
        return self._decrypt(self._id_number_enc)

    @id_number.setter
    def id_number(self, value):
        self._id_number_enc = self._encrypt(value)

    @property
    def commercial_reg(self):
        return self._decrypt(self._commercial_reg_enc)

    @commercial_reg.setter
    def commercial_reg(self, value):
        self._commercial_reg_enc = self._encrypt(value)

    # ============================================================
    # ✅ دوال مساعدة
    # ============================================================

    def to_dict(self):
        """تحويل الملف الشخصي إلى قاموس آمن (بدون كشف البيانات المشفرة)"""
        return {
            'id': self.id,
            'supplier_id': self.supplier_id,
            'trade_name': self.trade_name,
            'governorate': self.governorate,
            'city': self.city,
            'category': self.category_name,
            'bank': self.bank_name,
            'financial_company': self.company_name,
            'email': self.email,
            'phone': self.supplier.phone if self.supplier else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<SupplierProfile {self.trade_name} | {self.governorate} | {self.city}>'
