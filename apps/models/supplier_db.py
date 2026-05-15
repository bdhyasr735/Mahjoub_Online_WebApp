# coding: utf-8
from apps import db
from datetime import datetime

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    
    id = db.Column(db.Integer, primary_key=True)
    sovereign_id = db.Column(db.String(50), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    owner_name = db.Column(db.String(150), nullable=False)
    trade_name = db.Column(db.String(150), unique=True, nullable=False)
    shop_phone = db.Column(db.String(20), nullable=False)
    
    province = db.Column(db.String(50))
    district = db.Column(db.String(50))
    address_detail = db.Column(db.Text)
    
    fin_type = db.Column(db.String(20))
    bank_name = db.Column(db.String(100))
    bank_acc = db.Column(db.String(50))
    activity_type = db.Column(db.String(50))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
