# core/models/vendor.py

from core import db 

class Vendor(db.Model):
    __tablename__ = 'vendors'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # --- حقول الهوية السيادية لـ "سوقك الذكي" ---
    # هذا الحقل سيخزن القيمة MAH-9631، MAH-9632 إلخ
    supplier_id = db.Column(db.String(50), unique=True)
    
    trade_name = db.Column(db.String(150))
    owner_name = db.Column(db.String(150))
    phone = db.Column(db.String(20))
    
    # الرقم السيادي للمحفظة (W-MAH-9631)
    e_wallet = db.Column(db.String(100), unique=True)
    
    # حقول الأرصدة المالية الثلاثة
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
    
    # البيانات البنكية
    bank_name = db.Column(db.String(100))
    bank_acc = db.Column(db.String(100))
    fin_type = db.Column(db.String(50))
    
    created_at = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f'<Vendor {self.trade_name} - {self.supplier_id}>'

# نموذج طلبات السحب (لضمان اكتمال الترسانة المالية)
class WithdrawRequest(db.Model):
    __tablename__ = 'withdraw_requests'
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'))
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10)) # YER, SAR, USD
    status = db.Column(db.String(20), default='pending') # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=db.func.now())
