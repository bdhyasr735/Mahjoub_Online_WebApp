# 📂 apps/models/exchange_db.py
from apps.extensions import db
from datetime import datetime

class ExchangeRate(db.Model):
    __tablename__ = 'exchange_rates'
    
    id = db.Column(db.Integer, primary_key=True)
    currency_code = db.Column(db.String(5), unique=True, nullable=False) # e.g., 'USD', 'YER'
    rate_to_sar = db.Column(db.Numeric(18, 4), nullable=False) # سعر الصرف مقابل الريال السعودي
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_updated_by = db.Column(db.String(100)) 

    @staticmethod
    def get_rate(currency_code):
        rate = ExchangeRate.query.filter_by(currency_code=currency_code).first()
        return rate.rate_to_sar if rate else 1.0
