from core import db
from datetime import datetime
from flask_login import UserMixin

class Supplier(db.Model, UserMixin):
    __tablename__ = 'supplier'
    id = db.Column(db.Integer, primary_key=True)
    
    # بيانات الدخول والتعميد
    name = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    activity_type = db.Column(db.String(100))
    
    # 🛡️ نظام الرقابة والاعتماد
    is_approved = db.Column(db.Boolean, default=False) 
    status = db.Column(db.String(20), default='pending') 
    
    # تفاصيل المنشأة والموقع التيهامي
    trade_name = db.Column(db.String(200))
    full_name = db.Column(db.String(200))
    province = db.Column(db.String(100)) 
    district = db.Column(db.String(100)) 
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True, nullable=False)

    # 💰 النظام المالي المتعدد (تم التعديل ليتوافق مع الداشبورد)
    wallet_balance = db.Column(db.Float, default=0.0) # الرصيد الإجمالي
    wallet_usd = db.Column(db.Float, default=0.0)    # محفظة الدولار
    wallet_sar = db.Column(db.Float, default=0.0)    # محفظة السعودي
    wallet_yer = db.Column(db.Float, default=0.0)    # محفظة اليمني
    
    bank_name = db.Column(db.String(100))
    bank_acc = db.Column(db.String(100))
    fin_type = db.Column(db.String(50))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # علاقة الربط بالمنتجات
    products = db.relationship('Product', backref='supplier_owner', lazy=True, cascade="all, delete-orphan")

    @property
    def sovereign_id(self):
        """توليد الرقم السيادي للمحفظة MAH-9046"""
        return f"MAH-9046{self.id}"

    @property
    def approval_label(self):
        return "معتمد ✅" if self.is_approved else "بانتظار المراجعة ⏳"

    def __repr__(self):
        return f'<Supplier: {self.name} | Wallet: {self.sovereign_id}>'
