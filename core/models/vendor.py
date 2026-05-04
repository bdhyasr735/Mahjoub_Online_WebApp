# core/models/vendor.py
from core import db 
from datetime import datetime

class Vendor(db.Model):
    __tablename__ = 'vendors'
    # هذا السطر يمنع الخطأ sqlalchemy.exc.InvalidRequestError ويسمح بتحديث الجدول
    __table_args__ = {'extend_existing': True} 
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # --- حقول الهوية السيادية لـ "سوقك الذكي" ---
    # المعرف السيادي (MAH-963)
    supplier_id = db.Column(db.String(50), unique=True, nullable=True) 
    
    trade_name = db.Column(db.String(150))
    owner_name = db.Column(db.String(150))
    phone = db.Column(db.String(20))
    
    # المحفظة السيادية (W-MAH)
    e_wallet = db.Column(db.String(100), unique=True)
    
    # حقول الأرصدة المالية السيادية (دعم العملات الثلاث)
    balance_yer = db.Column(db.Float, default=0.0)
    balance_sar = db.Column(db.Float, default=0.0)
    balance_usd = db.Column(db.Float, default=0.0)
    
    # البيانات الجغرافية والنشاط
    id_type = db.Column(db.String(50))
    id_card_number = db.Column(db.String(100))
    activity_type = db.Column(db.String(100))
    province = db.Column(db.String(100))
    district = db.Column(db.String(100))
    address_detail = db.Column(db.Text)
    
    # البيانات البنكية والربط المالي
    bank_name = db.Column(db.String(100))
    bank_acc = db.Column(db.String(100))
    fin_type = db.Column(db.String(50))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # إضافة علاقة عكسية ليسهل الوصول للمستخدم من المورد والعكس
    user = db.relationship('User', backref=db.backref('vendor_profile', uselist=False))

    def __repr__(self):
        return f'<Vendor {self.trade_name} - {self.supplier_id}>'

class WithdrawRequest(db.Model):
    __tablename__ = 'withdraw_requests'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'))
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10)) # YER, SAR, USD
    status = db.Column(db.String(20), default='pending') 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # علاقة للوصول لبيانات المورد من طلب السحب
    vendor = db.relationship('Vendor', backref=db.backref('withdrawals', lazy=True))
