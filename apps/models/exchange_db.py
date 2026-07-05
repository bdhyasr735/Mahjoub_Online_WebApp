# 📂 apps/models/exchange_db.py
import os
from datetime import datetime
from cryptography.fernet import Fernet
from apps.extensions import db

class ExchangeRate(db.Model):
    __tablename__ = 'exchange_rates'
    
    # [فهرسة الأداء]: تحسين سرعة الاستعلامات الأساسية
    __table_args__ = (
        db.Index('idx_exch_currency_code', 'currency_code'),
        db.Index('idx_exch_updated_at', 'updated_at'),
        {'extend_existing': True}
    )
    
    id = db.Column(db.Integer, primary_key=True)
    currency_code = db.Column(db.String(5), unique=True, nullable=False)
    rate_to_sar = db.Column(db.Numeric(18, 4), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # [التشفير السيادي]: حقل التتبع مشفر لحماية هوية المسؤولين
    _last_updated_by_enc = db.Column(db.String(255), nullable=True)

    # --- نظام التشفير ---
    @staticmethod
    def _get_key():
        key = os.environ.get('ENCRYPTION_KEY')
        return key.encode() if key else b'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8Vq='

    @property
    def last_updated_by(self):
        """فك تشفير اسم المسؤول عند العرض."""
        if not self._last_updated_by_enc: return None
        try:
            return Fernet(self._get_key()).decrypt(self._last_updated_by_enc.encode()).decode()
        except Exception: 
            return "غير معروف"

    @last_updated_by.setter
    def last_updated_by(self, value):
        """تشفير اسم المسؤول قبل التخزين."""
        if value:
            self._last_updated_by_enc = Fernet(self._get_key()).encrypt(str(value).encode()).decode()

    @staticmethod
    def get_rate(currency_code):
        rate = ExchangeRate.query.filter_by(currency_code=currency_code).first()
        return rate.rate_to_sar if rate else 1.0

    def __repr__(self):
        return f'<ExchangeRate {self.currency_code}: {self.rate_to_sar}>'
