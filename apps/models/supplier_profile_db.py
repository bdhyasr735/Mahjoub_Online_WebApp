# coding: utf-8
# 📂 apps/models/supplier_profile_db.py

from apps.extensions import db  # تم التعديل
from cryptography.fernet import Fernet
import os

class SupplierProfile(db.Model):
    __tablename__ = 'supplier_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    # الفهرسة والربط مع المورد
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False, unique=True, index=True)
    
    # معلومات النشاط مع الـ Index للبحث السريع
    trade_name = db.Column(db.String(150), index=True)
    email = db.Column(db.String(150), index=True)
    
    # بيانات حساسة (مشفرة)
    _bank_account_enc = db.Column(db.String(255), nullable=True)
    _id_number_enc = db.Column(db.String(255), nullable=True)
    
    # العنوان (فهرسة للتقارير)
    governorate = db.Column(db.String(100), index=True)
    city = db.Column(db.String(100), index=True)
    
    # الربط السيادي
    supplier = db.relationship('Supplier', back_populates='supplier_profile')

    # --- نظام التشفير ---
    @staticmethod
    def _get_key():
        return os.environ.get('ENCRYPTION_KEY', 'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8Vq=').encode()

    @property
    def bank_account(self):
        if not self._bank_account_enc: return None
        try:
            return Fernet(self._get_key()).decrypt(self._bank_account_enc.encode()).decode()
        except: return None

    @bank_account.setter
    def bank_account(self, value):
        if value:
            self._bank_account_enc = Fernet(self._get_key()).encrypt(str(value).encode()).decode()

    @property
    def id_number(self):
        if not self._id_number_enc: return None
        try:
            return Fernet(self._get_key()).decrypt(self._id_number_enc.encode()).decode()
        except: return None

    @id_number.setter
    def id_number(self, value):
        if value:
            self._id_number_enc = Fernet(self._get_key()).encrypt(str(value).encode()).decode()

    def __repr__(self):
        return f'<Profile {self.trade_name}>'
