# coding: utf-8
# 📂 apps/models/financial_db.py - الميزان المالي السيادي (مؤمن ومفهرس للتدقيق اللحظي)

from apps.extensions import db
from datetime import datetime
from apps.utils.security import AESCipher

class ExchangeRate(db.Model):
    __tablename__ = 'exchange_rates'
    
    id = db.Column(db.Integer, primary_key=True)
    # ⚡ فهرسة رمز العملة للوصول السريع (الاستعلام الأكثر تكراراً)
    currency_code = db.Column(db.String(3), unique=True, nullable=False, index=True)
    rate_to_sar = db.Column(db.Numeric(18, 6), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)

    @classmethod
    def get_rate(cls, currency_code):
        currency_code = currency_code.upper()
        if currency_code == 'SAR':
            return 1.0
        record = cls.query.filter_by(currency_code=currency_code).first()
        return float(record.rate_to_sar) if record else 1.0

class FinancialLog(db.Model):
    __tablename__ = 'financial_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    # ⚡ فهرسة أنواع العمليات للتقارير الفورية
    operation_type = db.Column(db.String(50), nullable=False, index=True)
    sar_value = db.Column(db.Numeric(18, 2), nullable=False)
    
    # ⚡ فهرسة order_id للتدقيق السريع (Audit)
    order_id = db.Column(db.String(100), nullable=True, index=True)
    
    # 🔐 تشفير تفاصيل الحركة (لأنها قد تحتوي على تفاصيل حساسة)
    _details = db.Column('details', db.String(255))
    
    # ⚡ فهرسة الزمن للتقارير الدورية (يومية/شهرية)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    @property
    def details(self):
        return AESCipher.decrypt(self._details) if self._details else ""
        
    @details.setter
    def details(self, value):
        self._details = AESCipher.encrypt(str(value))
