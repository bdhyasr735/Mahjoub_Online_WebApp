# coding: utf-8
# 📂 apps/models/supplier_profile_db.py

import os
from cryptography.fernet import Fernet
from apps.extensions import db

class SupplierProfile(db.Model):
    __tablename__ = 'supplier_profiles'
    
    # [صمام الأمان]: فهرسة مسمّاة لضمان سرعة الاستعلامات
    __table_args__ = (
        db.Index('idx_prof_supplier_id', 'supplier_id'),
        db.Index('idx_prof_trade_name', 'trade_name'),
        db.Index('idx_prof_email', 'email'),
        db.Index('idx_prof_gov', 'governorate'),
        db.Index('idx_prof_city', 'city'),
        db.Index('idx_prof_address', 'address'),
        db.Index('idx_prof_category', 'category'),
        {'extend_existing': True}
    )
    
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False, unique=True)
    
    # ✅ حقول غير مشفرة (للسرعة والبحث)
    trade_name = db.Column(db.String(150))
    governorate = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    category = db.Column(db.String(100), nullable=True)
    
    # ✅ [تشفير سيادي]: جميع البيانات الحساسة مشفرة
    _email_enc = db.Column(db.String(255), nullable=True)
    _address_enc = db.Column(db.String(500), nullable=True)
    _description_enc = db.Column(db.Text, nullable=True)
    _bank_account_enc = db.Column(db.String(255), nullable=True)
    _id_number_enc = db.Column(db.String(255), nullable=True)
    _bank_name_enc = db.Column(db.String(255), nullable=True)        # ✅ اسم البنك
    _company_name_enc = db.Column(db.String(255), nullable=True)     # ✅ اسم الشركة
    _commercial_reg_enc = db.Column(db.String(255), nullable=True)   # ✅ السجل التجاري
    
    # [التحميل المتصل]: استخدام 'joined' يضمن جلب بيانات المورد في نفس الاستعلام
    supplier = db.relationship(
        'Supplier', 
        back_populates='supplier_profile',
        lazy='joined' 
    )

    # --- نظام التشفير (AES-256) ---
    @staticmethod
    def _get_key():
        return os.environ.get('ENCRYPTION_KEY', 'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8Vq=').encode()

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
    # ✅ Properties المشفرة
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
    def bank_name(self):
        return self._decrypt(self._bank_name_enc)
    
    @bank_name.setter
    def bank_name(self, value):
        self._bank_name_enc = self._encrypt(value)

    @property
    def company_name(self):
        return self._decrypt(self._company_name_enc)
    
    @company_name.setter
    def company_name(self, value):
        self._company_name_enc = self._encrypt(value)

    @property
    def commercial_reg(self):
        return self._decrypt(self._commercial_reg_enc)
    
    @commercial_reg.setter
    def commercial_reg(self, value):
        self._commercial_reg_enc = self._encrypt(value)

    def __repr__(self):
        return f'<Profile {self.trade_name} | {self.governorate} | {self.city} | {self.category}>'
