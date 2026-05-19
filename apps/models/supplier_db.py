# coding: utf-8
# 🔑 مستند النموذج الحوكمي للموردين - منصة محجوب أونلاين 2026

import random  # 🧠 استيراد مطلوب للمحرك الداخلي عند حدوث استثناء في التوليد
from apps import db
from datetime import datetime
from sqlalchemy.orm import validates

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    
    id = db.Column(db.Integer, primary_key=True)
    sovereign_id = db.Column(db.String(50), unique=True, nullable=False, index=True) 
    wallet_code = db.Column(db.String(50), unique=True, nullable=False)  # 💳 العمود المطلوب لربط كود المحفظة برمزها التتابعي المستقر
    
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)  # 🔒 الحقل الآمن المعتمد لتخزين الهاش المقابل لـ hashed_password
    identity_type = db.Column(db.String(50), nullable=False)    
    identity_number = db.Column(db.String(50), unique=True, nullable=False)  
    identity_image = db.Column(db.String(255))   
    
    owner_name = db.Column(db.String(150), unique=True, nullable=False)
    owner_phone = db.Column(db.String(20), unique=True, nullable=False)       
    trade_name = db.Column(db.String(150), unique=True, nullable=False)
    shop_phone = db.Column(db.String(20), unique=True, nullable=False)
    activity_type = db.Column(db.String(50))     
    
    province = db.Column(db.String(50))
    district = db.Column(db.String(50))
    address_detail = db.Column(db.Text)
    
    fin_type = db.Column(db.String(20))          
    bank_name = db.Column(db.String(100))        
    bank_acc = db.Column(db.String(50), unique=True, nullable=False)          
    
    status = db.Column(db.String(20), nullable=False, default='pending') 
    rank_grade = db.Column(db.String(20), nullable=False, default='ريادي') 
    registration_source = db.Column(db.String(30), nullable=False, default='الموقع الخارجي') 
    
    created_by_id = db.Column(db.Integer, nullable=True)  
    updated_by_id = db.Column(db.Integer, nullable=True)  

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) 
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow) 

    @property
    def state_title(self):
        sovereign_matrix = {
            'ريادي': {'active': 'مُطلق', 'pending': 'مراجعة', 'suspended': 'محتجز'},
            'سيادي': {'active': 'نافذ / مُهيمِن', 'pending': 'مراجعة الصلاحية', 'suspended': 'مُقيد / مجمد السيادة'},
            'ملكي': {'active': 'حَصين', 'pending': 'مستقر / صيانة خاصة', 'suspended': 'معلق الحصانة'}
        }
        current_rank_dict = sovereign_matrix.get(self.rank_grade, sovereign_matrix['ريادي'])
        return current_rank_dict.get(self.status, 'تحت التدقيق السيادي')

    @validates('username', 'identity_number', 'owner_name', 'owner_phone', 'trade_name', 'shop_phone', 'bank_acc')
    def validate_sovereign_fields(self, key, value):
        clean_value = str(value).strip() if value is not None else ""
        if not clean_value:
            raise ValueError(f"خطأ حوكمي صارم: الحقل السيادي ({key}) لا يمكن أن يكون فارغاً.")
        return clean_value

    # 👑 المحرك الداخلي السلس للتوليد الفوري والمحمي
    @staticmethod
    def generate_next_sovereign_id():
        """ استعلام مباشر وسريع لجلب المعرف التالي """
        last_supplier = Supplier.query.order_by(Supplier.id.desc()).first()
        if last_supplier and last_supplier.sovereign_id:
            try:
                parts = last_supplier.sovereign_id.split('MAH963')
                last_num = int(parts[-1])
                return f"SUP-MAH963{last_num + 1}"
            except (ValueError, IndexError):
                return f"SUP-MAH963{random.randint(100, 999)}"
        return "SUP-MAH9631"

    def to_dict(self):
        return {
            "id": self.id,
            "sovereign_id": self.sovereign_id,
            "wallet_code": self.wallet_code,
            "username": self.username,
            "owner_name": self.owner_name,
            "trade_name": self.trade_name,
            "shop_phone": self.shop_phone,
            "rank_grade": self.rank_grade,
            "status": self.status,
            "state_title": self.state_title  
        }
