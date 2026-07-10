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
        {'extend_existing': True}
    )
    
    id = db.Column(db.Integer, primary_key=True)
    # التأكد من وجود unique=True لضمان علاقة One-to-One
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False, unique=True)
    
    trade_name = db.Column(db.String(150))
    email = db.Column(db.String(150))
    
    # [التشفير السيادي]: بيانات حساسة مشفرة بـ AES
    _bank_account_enc = db.Column(db.String(255), nullable=True)
    _id_number_enc = db.Column(db.String(255), nullable=True)
    
    governorate = db.Column(db.String(100))
    city = db.Column(db.String(100))
    
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

    @property
    def bank_account(self):
        """فك التشفير عند الاستدعاء"""
        if not self._bank_account_enc: return None
        try:
            return Fernet(self._get_key()).decrypt(self._bank_account_enc.encode()).decode()
        except: return None

    @bank_account.setter
    def bank_account(self, value):
        """تشفير الحساب البنكي قبل التخزين"""
        if value:
            self._bank_account_enc = Fernet(self._get_key()).encrypt(str(value).encode()).decode()

    @property
    def id_number(self):
        """فك التشفير عند الاستدعاء"""
        if not self._id_number_enc: return None
        try:
            return Fernet(self._get_key()).decrypt(self._id_number_enc.encode()).decode()
        except: return None

    @id_number.setter
    def id_number(self, value):
        """تشفير رقم الهوية قبل التخزين"""
        if value:
            self._id_number_enc = Fernet(self._get_key()).encrypt(str(value).encode()).decode()

    def __repr__(self):
        return f'<Profile {self.trade_name}>'
