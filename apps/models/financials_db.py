# coding: utf-8
# 📂 apps/models/financials_db.py (النسخة النهائية مع الربط السيادي)

import os
from datetime import datetime
from cryptography.fernet import Fernet
from apps.extensions import db

class OrderFinancial(db.Model):
    """المركز المالي للطلبات: يربط الطلب بالمورد ويشفر البيانات الحساسة."""
    __tablename__ = 'order_financials'

    __table_args__ = (
        db.Index('idx_fin_order_id', 'order_id'),
        db.Index('idx_fin_supplier_id', 'supplier_id'),
        db.Index('idx_fin_settlement', 'settlement_status'),
        db.Index('idx_fin_created', 'created_at'),
        # الربط السيادي للفهرسة
        db.Index('idx_fin_transaction', 'transaction_id'),
        {'extend_existing': True}
    )

    # 1. المعرفات والربط
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(100), db.ForeignKey('orders.id'), nullable=False, unique=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    
    # ربط سيادي بجدول الخزينة (دفتر الأستاذ العام)
    transaction_id = db.Column(db.Integer, db.ForeignKey('wallet_transactions.id'), nullable=True)
    
    # 2. المبالغ المالية (مشفرة لحماية الخصوصية التجارية)
    _supplier_cost_enc = db.Column(db.String(255), nullable=False)
    _mahjoub_commission_enc = db.Column(db.String(255), nullable=False)
    _total_paid_enc = db.Column(db.String(255), nullable=False)
    shipping_fees = db.Column(db.Numeric(18, 2), default=0.00)
    
    # 3. حالة التسوية
    settlement_status = db.Column(db.String(20), default='pending') # pending, settled, failed
    
    # 4. توثيق زمني
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    settled_at = db.Column(db.DateTime, nullable=True)

    # [العلاقات]
    order = db.relationship('Order', back_populates='financials')
    supplier = db.relationship('Supplier', back_populates='financials')
    transaction = db.relationship('WalletTransaction', backref='order_financials')

    # --- نظام التشفير (AES) ---
    @staticmethod
    def _get_key():
        key = os.environ.get('ENCRYPTION_KEY')
        return key.encode() if key else b'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8Vq='

    def _encrypt(self, value):
        f = Fernet(self._get_key())
        return f.encrypt(str(value).encode()).decode()

    def _decrypt(self, value):
        try:
            f = Fernet(self._get_key())
            return float(f.decrypt(value.encode()).decode())
        except: return 0.0

    # --- Properties للمبالغ المشفرة ---
    @property
    def supplier_cost(self): return self._decrypt(self._supplier_cost_enc)
    @supplier_cost.setter
    def supplier_cost(self, value): self._supplier_cost_enc = self._encrypt(value)

    @property
    def mahjoub_commission(self): return self._decrypt(self._mahjoub_commission_enc)
    @mahjoub_commission.setter
    def mahjoub_commission(self, value): self._mahjoub_commission_enc = self._encrypt(value)

    @property
    def total_paid(self): return self._decrypt(self._total_paid_enc)
    @total_paid.setter
    def total_paid(self, value): self._total_paid_enc = self._encrypt(value)

    @property
    def amount(self): return self.total_paid

    def calculate_net_profit(self):
        return self.mahjoub_commission

    def __repr__(self):
        return f'<OrderFinancial OrderID: {self.order_id} | Status: {self.settlement_status}>'
