# coding: utf-8
# 📂 apps/models/supplier_db.py - (النسخة النهائية مع نظام الأكواد الآلي)

from apps.extensions import db
from apps.utils.security import AESCipher
from apps.config.constants import RANKS, STATUSES
from datetime import datetime

class Supplier(db.Model):
    __tablename__ = 'suppliers'

    # المعرف الرئيسي
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # --- حقول البحث السريع ---
    search_name = db.Column(db.String(150), index=True, nullable=True)
    search_phone = db.Column(db.String(20), index=True, nullable=True)

    # --- حقول البيانات ---
    sovereign_id = db.Column(db.String(100), nullable=True) 
    wallet_code = db.Column(db.String(50), nullable=True)
    sovereign_id_enc = db.Column(db.String(255), unique=True, nullable=True)
    
    # حقول إجبارية للمنطق
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # --- الحقول المشفرة ---
    trade_name_enc = db.Column(db.String(255), nullable=True) 
    owner_name_enc = db.Column(db.String(255), nullable=True)
    owner_phone_enc = db.Column(db.String(255), nullable=True)
    shop_phone_enc = db.Column(db.String(255), nullable=True)
    id_type_enc = db.Column(db.String(255), nullable=True)
    supply_category_enc = db.Column(db.String(255), nullable=True)
    province_enc = db.Column(db.String(255), nullable=True)
    district_enc = db.Column(db.String(255), nullable=True)
    address_detail_enc = db.Column(db.Text, nullable=True)
    financial_company_enc = db.Column(db.String(255), nullable=True)
    bank_name_enc = db.Column(db.String(255), nullable=True)
    bank_acc_enc = db.Column(db.String(255), nullable=True)
    
    status = db.Column(db.String(20), default=STATUSES[0], nullable=True)
    rank_grade = db.Column(db.String(20), default=RANKS[1], nullable=True)
    status_reason = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)

    # 🔗 الربط: نستخدم back_populates لربط صريح مع SupplierWallet
    wallet = db.relationship('SupplierWallet', back_populates='supplier', uselist=False)

    # --- نظام توليد الأكواد الآلي (Mahjoub Bridge Standard) ---
    def generate_codes(self):
        """توليد الأكواد الثابتة بناءً على الـ ID بعد حفظه في قاعدة البيانات"""
        if self.id:
            self.sovereign_id = f"SUP-MAH963{self.id}"
            self.wallet_code = f"WEL-MAH963{self.id}"
            self.sovereign_id_enc = AESCipher.encrypt(self.sovereign_id)
            db.session.add(self)

    # --- بوابات التشفير ---
    def _decrypt(self, value): return AESCipher.decrypt(value) if value else None

    @property
    def trade_name(self): return self._decrypt(self.trade_name_enc)
    @trade_name.setter
    def trade_name(self, value): 
        if value:
            self.trade_name_enc = AESCipher.encrypt(str(value))
            self.search_name = str(value)[:150]

    @property
    def owner_phone(self): return self._decrypt(self.owner_phone_enc)
    @owner_phone.setter
    def owner_phone(self, value): 
        if value:
            self.owner_phone_enc = AESCipher.encrypt(str(value))
            self.search_phone = str(value)[:20]

    @property
    def shop_phone(self): return self._decrypt(self.shop_phone_enc)
    @shop_phone.setter
    def shop_phone(self, value): 
        if value: self.shop_phone_enc = AESCipher.encrypt(str(value))

    @property
    def owner_name(self): return self._decrypt(self.owner_name_enc)
    @owner_name.setter
    def owner_name(self, value): 
        if value: self.owner_name_enc = AESCipher.encrypt(str(value))

    @property
    def bank_acc(self): return self._decrypt(self.bank_acc_enc)
    @bank_acc.setter
    def bank_acc(self, value): 
        if value: self.bank_acc_enc = AESCipher.encrypt(str(value))

    @property
    def financial_company(self): return self._decrypt(self.financial_company_enc)
    @financial_company.setter
    def financial_company(self, value): 
        if value: self.financial_company_enc = AESCipher.encrypt(str(value))
