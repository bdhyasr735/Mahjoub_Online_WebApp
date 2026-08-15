# coding: utf-8
# 📂 apps/models/treasury_db.py

import os
from datetime import datetime
from cryptography.fernet import Fernet
from apps.extensions import db

class TreasuryEntry(db.Model):
    """سجل الخزينة المركزية - سجل غير قابل للتعديل لضمان المطابقة المالية (SAR)"""
    __tablename__ = 'treasury_entries'

    # [فهرسة متقدمة]: لضمان سرعة التقارير المالية والبحث عن الحركات والسندات
    __table_args__ = (
        db.Index('idx_treasury_type_date', 'entry_type', 'created_at'),
        db.Index('idx_treasury_owner', 'owner_type', 'owner_id'),
        db.Index('idx_treasury_ref', 'reference_number'),
        db.Index('idx_treasury_voucher', 'voucher_number'),
        {'extend_existing': True}
    )

    id = db.Column(db.Integer, primary_key=True)
    
    # تصنيف الحركة: (revenue_net, affiliate_payout, supplier_settlement, operational_cost, deposit)
    entry_type = db.Column(db.String(50), nullable=False) 
    
    # المبلغ بالريال السعودي (SAR) فقط
    amount = db.Column(db.Numeric(18, 2), nullable=False)
    
    # العملة
    currency = db.Column(db.String(10), default='SAR', nullable=False)

    # الربط المرجعي مع الطلبات والمحافظ
    order_id = db.Column(db.String(100), db.ForeignKey('orders.id'), nullable=True)
    reference_number = db.Column(db.String(80), nullable=True) 
    voucher_number = db.Column(db.String(50), unique=True, nullable=True)  # ✅ حقل رقم السند المضاف حديثاً
    
    # هوية الطرف المعني
    owner_type = db.Column(db.String(20), nullable=False) # 'supplier', 'affiliate', 'platform'
    owner_id = db.Column(db.Integer, nullable=False)
    
    # [التشفير السيادي]: وصف الحركة مشفر (لحماية خصوصية تفاصيل التعاملات المالية)
    _description_enc = db.Column(db.String(500), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # --- نظام التشفير الموحد ---
    @staticmethod
    def _get_key():
        key = os.environ.get('ENCRYPTION_KEY', 'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8V=')
        return key.encode()

    @property
    def description(self):
        if not self._description_enc:
            return None
        try:
            return Fernet(self._get_key()).decrypt(self._description_enc.encode()).decode()
        except:
            return None

    @description.setter
    def description(self, value):
        if value:
            self._description_enc = Fernet(self._get_key()).encrypt(str(value).encode()).decode()
        else:
            self._description_enc = None

    def to_dict(self):
        """عرض بيانات الخزينة بتنسيق آمن للمطابقة"""
        return {
            'id': self.id,
            'entry_type': self.entry_type,
            'amount': float(self.amount),
            'currency': self.currency,
            'order_id': self.order_id,
            'reference_number': self.reference_number,
            'voucher_number': self.voucher_number,
            'owner': f"{self.owner_type}_{self.owner_id}",
            'description': self.description,
            'date': self.created_at.isoformat()
        }

    def __repr__(self):
        return f"<Treasury {self.entry_type} | {self.amount} {self.currency} | Voucher: {self.voucher_number}>"
