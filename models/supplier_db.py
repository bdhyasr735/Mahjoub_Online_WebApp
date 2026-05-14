from datetime import datetime
from apps import db  # استيراد db المركزي المشترك

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    
    id = db.Column(db.Integer, primary_key=True)
    sovereign_id = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50))
    owner_name = db.Column(db.String(100))
    trade_name = db.Column(db.String(100), unique=True)
    shop_phone = db.Column(db.String(20))
    province = db.Column(db.String(50))
    district = db.Column(db.String(50))
    address_detail = db.Column(db.Text)
    finance_type = db.Column(db.String(50))
    bank_name = db.Column(db.String(100))
    bank_account = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
