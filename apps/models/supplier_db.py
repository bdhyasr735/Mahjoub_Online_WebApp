# coding: utf-8
# 🔑 مستند النموذج الحوكمي المشفر للموردين - منصة محجوب أونلاين 2026

import random
import os
from apps.extensions import db
from datetime import datetime
from sqlalchemy.orm import validates
from apps.utils.security import AESCipher # مفترض وجوده في ملف الأمان

# تهيئة مشفر البيانات
cipher = AESCipher(os.getenv('ENCRYPTION_KEY', 'your-32-byte-key-here-must-be-secure'))

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    
    id = db.Column(db.Integer, primary_key=True)
    sovereign_id = db.Column(db.String(50), unique=True, nullable=False, index=True) 
    wallet_code = db.Column(db.String(50), unique=True, nullable=False)
    
    # حقول مشفرة (تخزين Ciphertext)
    _owner_name = db.Column(db.String(255), nullable=False)
    _owner_phone = db.Column(db.String(255), nullable=False)
    _trade_name = db.Column(db.String(255), nullable=False)
    _shop_phone = db.Column(db.String(255), nullable=False)
    _bank_acc = db.Column(db.String(255), nullable=False)
    
    # حقول التصنيف والتعلم الذكي
    category = db.Column(db.String(50), default='عام') 
    behavior_score = db.Column(db.Float, default=100.0)
    total_transactions = db.Column(db.Integer, default=0)
    
    # حقول إدارية
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    identity_type = db.Column(db.String(50), nullable=False)   
    identity_number = db.Column(db.String(50), unique=True, nullable=False)  
    identity_image = db.Column(db.String(255))   
    activity_type = db.Column(db.String(50))     
    province = db.Column(db.String(50))
    district = db.Column(db.String(50))
    address_detail = db.Column(db.Text) 
    fin_type = db.Column(db.String(20))          
    bank_name = db.Column(db.String(100))        
    status = db.Column(db.String(20), nullable=False, default='pending') 
    rank_grade = db.Column(db.String(20), nullable=False, default='ريادي') 
    registration_source = db.Column(db.String(30), nullable=False, default='الموقع الخارجي') 
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # --- خصائص التشفير الذكي (Properties) ---

    @property
    def owner_name(self): return cipher.decrypt(self._owner_name)
    @owner_name.setter
    def owner_name(self, value): self._owner_name = cipher.encrypt(value)

    @property
    def trade_name(self): return cipher.decrypt(self._trade_name)
    @trade_name.setter
    def trade_name(self, value): self._trade_name = cipher.encrypt(value)

    # --- منطق التعلم الذكي ---

    def learn_from_interaction(self, is_positive):
        """نظام التعلم من سلوك البشر"""
        self.behavior_score += (0.5 if is_positive else -2.0)
        self.total_transactions += 1
        
        # التكيف التلقائي للفئة
        if self.behavior_score > 150: self.category = 'مورد استراتيجي'
        elif self.behavior_score < 50: self.category = 'مورد تحت المراقبة'
        db.session.commit()

    @property
    def get_smart_status(self):
        if self.behavior_score < 50: return "مورد عالي المخاطر"
        return self.state_title

    # --- الدوال الأساسية ---

    @property
    def balance(self):
        from apps.models.statement_db import SupplierStatement
        last = SupplierStatement.query.filter_by(supplier_id=self.id).order_by(SupplierStatement.created_at.desc()).first()
        return last.running_balance if last else 0.0

    @staticmethod
    def generate_next_sovereign_id():
        last = Supplier.query.order_by(Supplier.id.desc()).first()
        num = int(last.sovereign_id.split('MAH963')[-1]) + 1 if last else 1
        return f"SUP-MAH963{num}"

    def to_dict(self):
        return {
            "sovereign_id": self.sovereign_id,
            "trade_name": self.trade_name,
            "category": self.category,
            "behavior_score": self.behavior_score,
            "balance": self.balance,
            "status": self.get_smart_status
        }
