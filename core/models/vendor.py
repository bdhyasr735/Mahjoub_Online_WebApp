from core import db  
from datetime import datetime

class Vendor(db.Model):
    __tablename__ = 'vendors'

    # --- الحقول الأساسية ---
    id = db.Column(db.Integer, primary_key=True)
    
    # الربط مع المستخدم (User Model)
    # تم إزالة unique=True مؤقتاً لضمان مرونة النظام السيادي في مرحلة التأسيس
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # --- بيانات الهوية والملك والوثائق ---
    owner_name = db.Column(db.String(255), nullable=False)
    id_type = db.Column(db.String(100), nullable=False)
    id_card_number = db.Column(db.String(50), nullable=False)
    id_image_path = db.Column(db.String(500), nullable=True) 
    
    # --- بيانات المنشأة والنشاط ---
    trade_name = db.Column(db.String(255), nullable=False)
    activity_type = db.Column(db.String(100), nullable=False)
    
    # --- البيانات الجغرافية والاتصال ---
    province = db.Column(db.String(100), nullable=False)
    district = db.Column(db.String(100), nullable=False)
    address_detail = db.Column(db.String(500), nullable=False)
    phone = db.Column(db.String(20), nullable=False)

    # --- الربط المالي والسيادي ---
    e_wallet = db.Column(db.String(100), unique=True, nullable=False)
    fin_type = db.Column(db.String(50), default='banks')
    bank_name = db.Column(db.String(150), nullable=False)
    bank_acc = db.Column(db.String(100), nullable=False)

    # --- بيانات النظام ---
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_verified = db.Column(db.Boolean, default=True)

    # علاقة عكسية اختيارية للوصول لبيانات المستخدم بسهولة
    user = db.relationship('User', backref=db.backref('vendors', lazy=True))

    def __repr__(self):
        return f"<Vendor {self.trade_name} - Sovereign ID: {self.e_wallet}>"
