# coding: utf-8
# 📂 apps/models/supplier_db.py - النموذج السيادي المحصن بالكامل

from apps.extensions import db
from apps.utils.security import AESCipher
from datetime import datetime

class Supplier(db.Model):
    __tablename__ = 'suppliers'

    # المعرف الرئيسي
    id = db.Column(db.Integer, primary_key=True)
    
    # المعرف السيادي (مشفر AES-256)
    sovereign_id_enc = db.Column(db.String(255), unique=True, nullable=False)
    
    # بيانات الدخول
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # حقول البيانات المشفرة
    trade_name_enc = db.Column(db.String(255), nullable=False)
    owner_name_enc = db.Column(db.String(255), nullable=False)
    id_type_enc = db.Column(db.String(255)) # نوع الهوية
    supply_category_enc = db.Column(db.String(255)) # فئة التوريد
    owner_phone_enc = db.Column(db.String(255), nullable=False)
    shop_phone_enc = db.Column(db.String(255), nullable=False)
    province_enc = db.Column(db.String(255))
    district_enc = db.Column(db.String(255))
    address_detail_enc = db.Column(db.Text)
    financial_company_enc = db.Column(db.String(255)) 
    bank_name_enc = db.Column(db.String(255))
    bank_acc_enc = db.Column(db.String(255))
    
    # الحالات والرتب (نصوص للمنطق البرمجي)
    status = db.Column(db.String(20), default='قيد المراجعة')
    rank_grade = db.Column(db.String(20), default='ريادي')
    status_reason = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # --- بوابات التشفير الكاملة (AES-256) ---
    @property
    def sovereign_id(self): return AESCipher.decrypt(self.sovereign_id_enc)
    @sovereign_id.setter
    def sovereign_id(self, value): self.sovereign_id_enc = AESCipher.encrypt(str(value))

    @property
    def trade_name(self): return AESCipher.decrypt(self.trade_name_enc)
    @trade_name.setter
    def trade_name(self, value): self.trade_name_enc = AESCipher.encrypt(str(value))

    @property
    def owner_name(self): return AESCipher.decrypt(self.owner_name_enc)
    @owner_name.setter
    def owner_name(self, value): self.owner_name_enc = AESCipher.encrypt(str(value))

    @property
    def id_type(self): return AESCipher.decrypt(self.id_type_enc)
    @id_type.setter
    def id_type(self, value): self.id_type_enc = AESCipher.encrypt(str(value))

    @property
    def supply_category(self): return AESCipher.decrypt(self.supply_category_enc)
    @supply_category.setter
    def supply_category(self, value): self.supply_category_enc = AESCipher.encrypt(str(value))

    @property
    def owner_phone(self): return AESCipher.decrypt(self.owner_phone_enc)
    @owner_phone.setter
    def owner_phone(self, value): self.owner_phone_enc = AESCipher.encrypt(str(value))

    @property
    def shop_phone(self): return AESCipher.decrypt(self.shop_phone_enc)
    @shop_phone.setter
    def shop_phone(self, value): self.shop_phone_enc = AESCipher.encrypt(str(value))

    @property
    def province(self): return AESCipher.decrypt(self.province_enc)
    @province.setter
    def province(self, value): self.province_enc = AESCipher.encrypt(str(value))

    @property
    def district(self): return AESCipher.decrypt(self.district_enc)
    @district.setter
    def district(self, value): self.district_enc = AESCipher.encrypt(str(value))

    @property
    def address_detail(self): return AESCipher.decrypt(self.address_detail_enc)
    @address_detail.setter
    def address_detail(self, value): self.address_detail_enc = AESCipher.encrypt(str(value))

    @property
    def financial_company(self): return AESCipher.decrypt(self.financial_company_enc)
    @financial_company.setter
    def financial_company(self, value): self.financial_company_enc = AESCipher.encrypt(str(value))

    @property
    def bank_name(self): return AESCipher.decrypt(self.bank_name_enc)
    @bank_name.setter
    def bank_name(self, value): self.bank_name_enc = AESCipher.encrypt(str(value))

    @property
    def bank_acc(self): return AESCipher.decrypt(self.bank_acc_enc)
    @bank_acc.setter
    def bank_acc(self, value): self.bank_acc_enc = AESCipher.encrypt(str(value))

    # --- مصفوفة الصلاحيات السيادية ---
    def can_access(self, action):
        """التحقق من صلاحية الوصول بناءً على الحالة والرتبة"""
        if self.status in ['محظور', 'مرفوض']: 
            return False
        
        if self.status == 'قيد المراجعة': 
            return action == 'استعلام'
            
        if self.status == 'معلق': 
            return action in ['قراءة فقط', 'سجل العمليات']
            
        if self.status == 'نشط':
            if self.rank_grade == 'سيادي': 
                return True
            if self.rank_grade == 'ملكي': 
                return action in ['وصول كامل', 'حجم تجاري كبير', 'قياسي', 'قراءة فقط', 'سجل العمليات']
            if self.rank_grade == 'ريادي': 
                return action in ['قياسي', 'قراءة فقط', 'سجل العمليات']
        
        return False
