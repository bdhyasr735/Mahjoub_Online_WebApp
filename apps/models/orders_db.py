# coding: utf-8
# 📂 apps/models/orders_db.py

import os
from datetime import datetime
from cryptography.fernet import Fernet
from apps.extensions import db

def get_cipher():
    key = os.getenv('ENCRYPTION_KEY', 'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8Vq=')
    return Fernet(key.encode())

cipher = get_cipher()

class Order(db.Model):
    """موديل الطلبات: المحرك التشغيلي الذي يربط العميل بالمورد والمسوق."""
    __tablename__ = 'orders'

    __table_args__ = (
        db.Index('idx_ord_supplier_id', 'supplier_id'),
        db.Index('idx_ord_marketer_id', 'marketer_id'),
        db.Index('idx_ord_tracking_tag', 'tracking_tag'),
        db.Index('idx_ord_ref', 'order_reference'),
        db.Index('idx_ord_status', 'status'),
        db.Index('idx_ord_created', 'created_at'),
        {'extend_existing': True}
    )

    id = db.Column(db.String(100), primary_key=True)
    order_id_display = db.Column(db.String(50), nullable=True)
    
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=True)
    marketer_id = db.Column(db.Integer, db.ForeignKey('marketers.id'), nullable=True)
    
    tracking_tag = db.Column(db.String(100), nullable=True)
    order_reference = db.Column(db.String(100), unique=True, nullable=True)  # يمكن استخدامه كـ "رقم الطلب"
    
    total_price = db.Column(db.Numeric(18, 2), default=0.00)
    items_count = db.Column(db.Integer, default=0)
    status = db.Column(db.String(30), default='pending')
    
    # ✅ الحقول الجديدة للحالة المالية وحالة الشحن
    financial_status = db.Column(db.String(30), default='unpaid')
    fulfillment_status = db.Column(db.String(30), default='unfulfilled')
    
    _customer_name = db.Column(db.Text)
    _customer_phone = db.Column(db.Text)
    _customer_address = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    supplier = db.relationship('Supplier', back_populates='orders', lazy='joined')
    marketer = db.relationship('Marketer', back_populates='orders', lazy='joined')
    
    items = db.relationship(
        'OrderItem', 
        back_populates='order', 
        cascade="all, delete-orphan", 
        lazy='joined'
    )
    
    financials = db.relationship(
        'OrderFinancial', 
        back_populates='order', 
        uselist=False, 
        cascade="all, delete-orphan", 
        lazy='joined'
    )

    @property
    def amount(self):
        return self.financials.total_paid if self.financials else 0.0

    @property
    def customer_name(self):
        try:
            return cipher.decrypt(self._customer_name.encode()).decode() if self._customer_name else "غير معروف"
        except Exception: return "خطأ في التشفير"

    @customer_name.setter
    def customer_name(self, value):
        self._customer_name = cipher.encrypt(str(value).encode()).decode()

    @property
    def customer_phone(self):
        try:
            return cipher.decrypt(self._customer_phone.encode()).decode() if self._customer_phone else None
        except Exception: return None

    @customer_phone.setter
    def customer_phone(self, value):
        if value: self._customer_phone = cipher.encrypt(str(value).encode()).decode()

    @property
    def customer_address(self):
        try:
            return cipher.decrypt(self._customer_address.encode()).decode() if self._customer_address else None
        except Exception: return None

    @customer_address.setter
    def customer_address(self, value):
        if value: self._customer_address = cipher.encrypt(str(value).encode()).decode()

    def to_dict(self):
        """تحويل الطلب إلى قاموس للاستخدام في الواجهة"""
        return {
            'id': self.id,
            'qid': self.id,
            'order_reference': self.order_reference,  # رقم الطلب الحقيقي
            'supplier_id': self.supplier_id,
            'status_code': self.status,
            'status_title': self.status.title() if self.status else 'غير معروف',
            'financial_status': self.financial_status,
            'fulfillment_status': self.fulfillment_status,
            'total_price': float(self.total_price) if self.total_price else 0.0,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'supplier_name': self.supplier.trade_name if self.supplier else 'غير مرتبط'
        }

    def __repr__(self):
        return f'<Order {self.order_id_display or self.id} | Status: {self.status} | Amount: {self.amount} SAR>'
