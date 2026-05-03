from core import db
from datetime import datetime

class Vendor(db.Model):
    __tablename__ = 'vendors'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # البيانات الأساسية للمورد
    owner_name = db.Column(db.String(150), nullable=False)
    trade_name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    
    # نظام الهوية السيادية والمحفظة
    # المعرف (ID): MAH-963
    # المحفظة (Wallet): W-MAH-963
    e_wallet = db.Column(db.String(100), unique=True, nullable=False)
    
    # الأرصدة متعددة العملات
    balance_yer = db.Column(db.Float, default=0.0) # ريال يمني
    balance_sar = db.Column(db.Float, default=0.0) # ريال سعودي
    balance_usd = db.Column(db.Float, default=0.0) # دولار أمريكي

    # وثائق الهوية والأرشفة
    id_type = db.Column(db.String(100), default='بطاقة شخصية')
    id_card_number = db.Column(db.String(100))
    activity_type = db.Column(db.String(100))
    
    # الموقع الجغرافي
    province = db.Column(db.String(100))
    district = db.Column(db.String(100))
    address_detail = db.Column(db.String(255))
    
    # الربط البنكي
    bank_name = db.Column(db.String(150))
    bank_acc = db.Column(db.String(100))
    fin_type = db.Column(db.String(50), default='banks') # banks or exchange

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Vendor {self.trade_name} - {self.e_wallet}>'

class WithdrawRequest(db.Model):
    __tablename__ = 'withdraw_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), nullable=False) # YER, SAR, USD
    status = db.Column(db.String(20), default='pending') # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
