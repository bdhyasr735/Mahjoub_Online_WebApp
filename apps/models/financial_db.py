# coding: utf-8
# 📂 apps/models/financial_db.py - مرجع الأسعار والرقابة المالية

from apps.extensions import db
from datetime import datetime

class ExchangeRate(db.Model):
    """جدول أسعار الصرف: يتحكم فيه المسؤول لتوحيد التحويلات"""
    __tablename__ = 'exchange_rates'
    
    id = db.Column(db.Integer, primary_key=True)
    currency_code = db.Column(db.String(3), unique=True, nullable=False) # SAR, USD, YER
    rate_to_sar = db.Column(db.Numeric(18, 6), nullable=False) # السعر مقابل الريال السعودي
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def get_rate(cls, currency_code):
        if currency_code.upper() == 'SAR':
            return 1.0
        record = cls.query.filter_by(currency_code=currency_code.upper()).first()
        return float(record.rate_to_sar) if record else 1.0

class FinancialLog(db.Model):
    """سجل المراجعة المالي: الصندوق الأسود لكل حركة مالية في المنصة"""
    __tablename__ = 'financial_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    operation_type = db.Column(db.String(50), nullable=False) # e.g., 'sale', 'adjustment'
    sar_value = db.Column(db.Numeric(18, 2), nullable=False) # القيمة الموحدة للمقارنة
    details = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
