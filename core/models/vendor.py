# core/models/vendor.py
from core import db
from datetime import datetime

class Vendor(db.Model):
    __tablename__ = 'vendors'

    id = db.Column(db.Integer, primary_key=True)
    # ربط المورد بحساب مستخدم للدخول إلى لوحة التحكم
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) 
    
    owner_name = db.Column(db.String(150), nullable=False)
    trade_name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    
    # المحفظة (Wallet): W-MAH-963
    e_wallet = db.Column(db.String(100), unique=True, nullable=False)
    
    balance_yer = db.Column(db.Float, default=0.0)
    balance_sar = db.Column(db.Float, default=0.0)
    balance_usd = db.Column(db.Float, default=0.0)

    id_type = db.Column(db.String(100), default='بطاقة شخصية')
    id_card_number = db.Column(db.String(100))
    # إضافة مسار صورة الهوية للأرشفة الضوئية
    id_image = db.Column(db.String(255), nullable=True) 
    
    activity_type = db.Column(db.String(100))
    
    province = db.Column(db.String(100))
    district = db.Column(db.String(100))
    address_detail = db.Column(db.String(255))
    
    bank_name = db.Column(db.String(150))
    bank_acc = db.Column(db.String(100))
    fin_type = db.Column(db.String(50), default='banks') 

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # علاقة عكسية لجلب بيانات المستخدم بسهولة
    user = db.relationship('User', backref=db.backref('vendor_profile', uselist=False))

    def __repr__(self):
        return f'<Vendor {self.trade_name} - {self.e_wallet}>'
