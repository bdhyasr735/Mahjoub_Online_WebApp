from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    id = db.Column(db.Integer, primary_key=True)
    sovereign_id = db.Column(db.String(100), unique=True, nullable=False) # المعرف الملكي
    trade_name = db.Column(db.String(150), nullable=False)
    tier = db.Column(db.String(50), default='مبتدئ') # (مبتدئ، احترافي، سيادي)
    status = db.Column(db.String(50), default='نشط')
    balance_yer = db.Column(db.Numeric(20, 2), default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
