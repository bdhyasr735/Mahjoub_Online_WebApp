# coding: utf-8
# 📂 apps/models/supplier_db.py - النموذج السيادي المحصن (جاهز للمليون سجل)

from apps.extensions import db
from apps.utils.security import AESCipher
from apps.config.constants import RANKS, STATUSES
from datetime import datetime

class Supplier(db.Model):
    __tablename__ = 'suppliers'

    # المعرف الرئيسي
    id = db.Column(db.Integer, primary_key=True)
    
    # --- حقول البحث السريع (فهارس غير مشفرة للبحث المليوني) ---
    # هذه الحقول تسهل البحث السريع دون التأثير على أمن البيانات المشفرة
    search_name = db.Column(db.String(150), index=True, nullable=False)
    search_phone = db.Column(db.String(20), index=True, nullable=False)

    # --- حقول التشفير السيادي ---
    sovereign_id_enc = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    trade_name_enc = db.Column(db.String(255), nullable=False)
    owner_name_enc = db.Column(db.String(255), nullable=False)
    id_type_enc = db.Column(db.String(255))
    supply_category_enc = db.Column(db.String(255))
    owner_phone_enc = db.Column(db.String(255), nullable=False)
    shop_phone_enc = db.Column(db.String(255), nullable=False)
    province_enc = db.Column(db.String(255))
    district_enc = db.Column(db.String(255))
    address_detail_enc = db.Column(db.Text)
    financial_company_enc = db.Column(db.String(255))
    bank_name_enc = db.Column(db.String(255))
    bank_acc_enc = db.Column(db.String(255))
    
    status = db.Column(db.String(20), default=STATUSES[0])
    rank_grade = db.Column(db.String(20), default=RANKS[1])
    status_reason = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # --- بوابات التشفير السيادية ---
    def _decrypt(self, value): return AESCipher.decrypt(value) if value else None

    # عند تعيين الاسم، نقوم بتحديث حقل البحث غير المشفر تلقائياً
    @property
    def trade_name(self): return self._decrypt(self.trade_name_enc)
    @trade_name.setter
    def trade_name(self, value): 
        self.trade_name_enc = AESCipher.encrypt(str(value))
        self.search_name = value # تحديث فهرس البحث

    @property
    def owner_phone(self): return self._decrypt(self.owner_phone_enc)
    @owner_phone.setter
    def owner_phone(self, value): 
        self.owner_phone_enc = AESCipher.encrypt(str(value))
        self.search_phone = value # تحديث فهرس البحث

    # ... (بقية الـ properties بنفس الطريقة السابقة)
    
    # احتفظ بـ باقي الـ properties كما هي في كودك الأصلي...
