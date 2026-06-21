# coding: utf-8
# 📂 apps/models/supplier_profile_db.py - الملف السيادي لبيانات الموردين (مؤمن ومفهرس)

from apps.extensions import db
from apps.utils.security import AESCipher
from apps.models.admin_db import AdminUser

class SupplierProfile(db.Model):
    __tablename__ = 'supplier_profiles'

    # المفاتيح الأساسية مفهرسة تلقائياً
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # ⚡ user_id مفهرس لأنه حقل الربط الأساسي للبحث عن البروفايل
    user_id = db.Column(db.Integer, db.ForeignKey('admin_users.id'), unique=True, nullable=False, index=True)
    
    # ⚡ wallet_code مفهرس لأنه سيتكرر كثيراً في عمليات المحفظة
    wallet_code = db.Column(db.String(50), nullable=True, index=True)

    # حقول مشفرة بـ AES-256 (لا يمكن فهرستها مباشرة، لذا نكتفي بتأمينها)
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

    user = db.relationship('AdminUser', back_populates='supplier_profile', lazy='joined')

    # --- نمط تشفير سيادي موحد ---
    def _encrypt(self, value):
        return AESCipher.encrypt(value) if value else None

    def _decrypt(self, value):
        return AESCipher.decrypt(value) if value else None

    # --- Properties ---
    @property
    def trade_name(self): return self._decrypt(self.trade_name_enc)
    @trade_name.setter
    def trade_name(self, v): self.trade_name_enc = self._encrypt(v)

    @property
    def owner_name(self): return self._decrypt(self.owner_name_enc)
    @owner_name.setter
    def owner_name(self, v): self.owner_name_enc = self._encrypt(v)

    @property
    def id_type(self): return self._decrypt(self.id_type_enc)
    @id_type.setter
    def id_type(self, v): self.id_type_enc = self._encrypt(v)

    @property
    def supply_category(self): return self._decrypt(self.supply_category_enc)
    @supply_category.setter
    def supply_category(self, v): self.supply_category_enc = self._encrypt(v)

    @property
    def province(self): return self._decrypt(self.province_enc)
    @province.setter
    def province(self, v): self.province_enc = self._encrypt(v)

    @property
    def district(self): return self._decrypt(self.district_enc)
    @district.setter
    def district(self, v): self.district_enc = self._encrypt(v)

    @property
    def address_detail(self): return self._decrypt(self.address_detail_enc)
    @address_detail.setter
    def address_detail(self, v): self.address_detail_enc = self._encrypt(v)

    @property
    def bank_name(self): return self._decrypt(self.bank_name_enc)
    @bank_name.setter
    def bank_name(self, v): self.bank_name_enc = self._encrypt(v)

    @property
    def bank_acc(self): return self._decrypt(self.bank_acc_enc)
    @bank_acc.setter
    def bank_acc(self, v): self.bank_acc_enc = self._encrypt(v)

    def __repr__(self):
        return f"<SupplierProfile for User ID: {self.user_id}>"
