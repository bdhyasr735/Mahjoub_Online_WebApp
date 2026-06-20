# coding: utf-8
# 📂 apps/models/supplier_profile_db.py - (البيانات التجارية المتقدمة للموردين - نسخة مشفرة سيادياً)

from apps.extensions import db
from apps.utils.security import AESCipher
from apps.models.admin_db import AdminUser # تم استيرادها في الأعلى لترتيب الكود

class SupplierProfile(db.Model):
    __tablename__ = 'supplier_profiles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # الربط المفتاحي الحوكمي مع الحساب الموحد
    user_id = db.Column(db.Integer, db.ForeignKey('admin_users.id'), unique=True, nullable=False)
    wallet_code = db.Column(db.String(50), nullable=True)

    # --- الحقول التجارية المشفرة ---
    trade_name_enc = db.Column(db.String(255), nullable=True) 
    owner_name_enc = db.Column(db.String(255), nullable=True)
    id_type_enc = db.Column(db.String(255), nullable=True)
    supply_category_enc = db.Column(db.String(255), nullable=True)
    province_enc = db.Column(db.String(255), nullable=True)
    district_enc = db.Column(db.String(255), nullable=True)
    address_detail_enc = db.Column(db.Text, nullable=True)
    financial_company_enc = db.Column(db.String(255), nullable=True)
    bank_name_enc = db.Column(db.String(255), nullable=True)
    bank_acc_enc = db.Column(db.String(255), nullable=True)

    # العلاقات البرمجية
    user = db.relationship('AdminUser', back_populates='supplier_profile', lazy='joined')

    # --- Properties لفك التشفير التلقائي (مثال للحقول الأساسية) ---
    @property
    def trade_name(self):
        return AESCipher.decrypt(self.trade_name_enc) if self.trade_name_enc else None

    @trade_name.setter
    def trade_name(self, value):
        self.trade_name_enc = AESCipher.encrypt(value) if value else None

    @property
    def owner_name(self):
        return AESCipher.decrypt(self.owner_name_enc) if self.owner_name_enc else None

    @owner_name.setter
    def owner_name(self, value):
        self.owner_name_enc = AESCipher.encrypt(value) if value else None

    @property
    def bank_acc(self):
        return AESCipher.decrypt(self.bank_acc_enc) if self.bank_acc_enc else None

    @bank_acc.setter
    def bank_acc(self, value):
        self.bank_acc_enc = AESCipher.encrypt(value) if value else None

    def __repr__(self):
        return f"<SupplierProfile for User ID: {self.user_id}>"
