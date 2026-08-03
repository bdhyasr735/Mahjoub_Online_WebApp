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
        db.Index('idx_ord_status', 'status_code'),
        db.Index('idx_ord_created', 'created_at'),
        {'extend_existing': True}
    )

    id = db.Column(db.String(100), primary_key=True)
    order_id_display = db.Column(db.String(50), nullable=True)
    
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=True)
    marketer_id = db.Column(db.Integer, db.ForeignKey('marketers.id'), nullable=True)
    
    tracking_tag = db.Column(db.String(100), nullable=True)
    order_reference = db.Column(db.String(100), unique=True, nullable=True)  # يستخدم كرقم الطلب للعرض
    
    total_price = db.Column(db.Numeric(18, 2), default=0.00)
    items_count = db.Column(db.Integer, default=0)
    
    # ✅ حقل الترقيم التسلسلي للطلب
    order_number = db.Column(db.Integer, nullable=True)
    
    # ✅ حقول الحالة بناءً على السكيما
    status_code = db.Column(db.String(30), default='pending')
    status_title = db.Column(db.String(50), default='قيد الانتظار')
    is_paid = db.Column(db.Boolean, default=False)
    
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
        return float(self.financials.total_paid) if self.financials and self.financials.total_paid else float(self.total_price or 0.0)

    @property
    def customer_name(self):
        if not self._customer_name:
            return "غير معروف"
        try:
            return cipher.decrypt(self._customer_name.encode()).decode()
        except Exception:
            # في حال كانت البيانات غير مشفرة نصياً في قواعد البيانات القديمة
            return str(self._customer_name)

    @customer_name.setter
    def customer_name(self, value):
        if value:
            self._customer_name = cipher.encrypt(str(value).encode()).decode()

    @property
    def customer_phone(self):
        if not self._customer_phone:
            return None
        try:
            return cipher.decrypt(self._customer_phone.encode()).decode()
        except Exception:
            return str(self._customer_phone)

    @customer_phone.setter
    def customer_phone(self, value):
        if value:
            self._customer_phone = cipher.encrypt(str(value).encode()).decode()

    @property
    def customer_address(self):
        if not self._customer_address:
            return None
        try:
            return cipher.decrypt(self._customer_address.encode()).decode()
        except Exception:
            return str(self._customer_address)

    @customer_address.setter
    def customer_address(self, value):
        if value:
            self._customer_address = cipher.encrypt(str(value).encode()).decode()

    def to_dict(self):
        """تحويل الطلب إلى قاموس للاستخدام في الواجهة"""
        return {
            'id': self.id,
            'qid': self.id,
            'order_reference': self.order_reference,
            'order_number': self.order_number,
            'supplier_id': self.supplier_id,
            'status_code': self.status_code,
            'status_title': self.status_title,
            'status_text': self.status_title or 'غير معروف',
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone,
            'customer_address': self.customer_address,
            'is_paid': self.is_paid,
            'total_price': float(self.total_price) if self.total_price else 0.0,
            'items_count': self.items_count or (len(self.items) if self.items else 0),
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'supplier_name': self.supplier.trade_name if self.supplier else 'غير مرتبط'
        }

    def __repr__(self):
        return f'<Order {self.order_id_display or self.id} | Status: {self.status_title} | Amount: {self.amount} SAR>'
