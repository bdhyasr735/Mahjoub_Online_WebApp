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
    order_reference = db.Column(db.String(100), unique=True, nullable=True)
    
    total_price = db.Column(db.Numeric(18, 2), default=0.00)
    items_count = db.Column(db.Integer, default=0)
    
    order_number = db.Column(db.Integer, nullable=True)
    
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
    
    # استخدام الأسماء المباشرة القياسية
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
            return str(self._customer_name)

    @customer_name.setter
    def customer_name(self, value):
        if value:
            self._customer_name = cipher.encrypt(str(value).encode()).decode()
        else:
            self._customer_name = None

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
        else:
            self._customer_phone = None

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
        else:
            self._customer_address = None

    @property
    def _id(self):
        return self.id

    @property
    def status(self):
        code_val = self.status_code or 'pending'
        title_val = self.status_title or 'قيد الانتظار'

        class StatusWrapper:
            def __init__(self, code, title):
                self.code = code
                self.title = title
            def __getitem__(self, item):
                return getattr(self, item, '')
            def __str__(self):
                return str(self.code)

        return StatusWrapper(code_val, title_val)

    @property
    def account(self):
        fullname_val = self.customer_name or 'عميل'

        class AccountInner:
            def __init__(self, fullname):
                self.fullname = fullname
                self.phone = None
                self.avatarUrl = None

        class AccountOuter:
            def __init__(self, fullname):
                self.account = AccountInner(fullname)

        return AccountOuter(fullname_val)

    @property
    def total_amount(self):
        return self.total_price

    @property
    def totalPrice(self):
        return self.total_price

    @property
    def shipping_address(self):
        return self.customer_address

    def to_dict(self):
        return {
            'id': self.id,
            '_id': self.id,
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
            'supplier_name': self.supplier.trade_name if self.supplier else 'غير مرتبط',
            'items': [item.to_dict() for item in self.items] if self.items else []
        }

    def __repr__(self):
        return f'<Order {self.order_id_display or self.id} | Status: {self.status_title} | Amount: {self.amount} SAR>'


class OrderItem(db.Model):
    """عناصر الطلب المرتبطة بجدول Order."""
    __tablename__ = 'order_items'

    __table_args__ = (
        {'extend_existing': True},
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.String(100), db.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    
    productId = db.Column(db.String(100), nullable=True)
    title = db.Column(db.String(255), nullable=True)
    qty = db.Column(db.Integer, default=1)
    price_per_unit = db.Column(db.Numeric(18, 2), default=0.00)
    subtotal = db.Column(db.Numeric(18, 2), default=0.00)
    sku = db.Column(db.String(100), nullable=True)
    _image_url = db.Column(db.Text, nullable=True)

    # استخدام الاسم المباشر للعلاقة المعاكسة
    order = db.relationship('Order', back_populates='items')

    @property
    def _id(self):
        return str(self.id)

    @property
    def price(self):
        return float(self.price_per_unit or 0.0)

    @property
    def quantity(self):
        return self.qty

    @property
    def totalPrice(self):
        return float(self.subtotal or (float(self.price_per_unit or 0.0) * self.qty))

    @property
    def productData(self):
        item_title = self.title or 'منتج'
        img_url = self._image_url

        class ImageWrapper:
            def __init__(self, url):
                self.fileUrl = url

        class ProductDataInner:
            def __init__(self, title, image_url):
                self.title = title
                self.slug = title
                self.image = ImageWrapper(image_url) if image_url else None

        return ProductDataInner(item_title, img_url)

    def to_dict(self):
        return {
            'id': self.id,
            '_id': str(self.id),
            'order_id': self.order_id,
            'productId': self.productId,
            'title': self.title,
            'qty': self.qty,
            'quantity': self.qty,
            'price': float(self.price_per_unit or 0.0),
            'price_per_unit': float(self.price_per_unit or 0.0),
            'subtotal': float(self.subtotal or 0.0),
            'totalPrice': float(self.subtotal or 0.0),
            'sku': self.sku,
            'productData': {
                'title': self.title,
                'slug': self.title,
                'image': {'fileUrl': self._image_url} if self._image_url else None
            }
        }
