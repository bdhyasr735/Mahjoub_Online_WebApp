# coding: utf-8
# 📂 apps/models/order_db.py

from apps.extensions import db
from apps.utils.security import AESCipher

class ProcessedOrder(db.Model):
    __tablename__ = 'processed_orders'

    # --- الأعمدة الأساسية ---
    id = db.Column(db.String(100), primary_key=True)  # QID
    order_id = db.Column(db.String(50))
    order_status = db.Column(db.String(50))
    financial_status = db.Column(db.String(50))
    fulfillment_status = db.Column(db.String(50))
    shipping_city = db.Column(db.String(100))
    shipping_street = db.Column(db.String(200))
    # مفتاح ربط مع المورد
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=True)

    # --- الحقول المشفرة (تخزن كـ String مشفر في DB) ---
    _total_price = db.Column('total_price', db.String(255))
    _customer_name = db.Column('customer_name', db.String(255))
    _customer_phone = db.Column('customer_phone', db.String(255))
    _customer_email = db.Column('customer_email', db.String(255))

    # --- Properties للتشفير وفك التشفير ---
    
    @property
    def total_price(self):
        val = AESCipher.decrypt(self._total_price)
        return float(val) if val else 0.0

    @total_price.setter
    def total_price(self, value):
        self._total_price = AESCipher.encrypt(str(value))

    @property
    def customer_name(self):
        return AESCipher.decrypt(self._customer_name) or ""

    @customer_name.setter
    def customer_name(self, value):
        self._customer_name = AESCipher.encrypt(str(value))

    @property
    def customer_phone(self):
        return AESCipher.decrypt(self._customer_phone) or ""

    @customer_phone.setter
    def customer_phone(self, value):
        self._customer_phone = AESCipher.encrypt(str(value))

    @property
    def customer_email(self):
        return AESCipher.decrypt(self._customer_email) or ""

    @customer_email.setter
    def customer_email(self, value):
        self._customer_email = AESCipher.encrypt(str(value))


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(100), db.ForeignKey('processed_orders.id'))
    product_title = db.Column(db.String(200))
    quantity = db.Column(db.Integer)
    _price = db.Column('price', db.String(255))

    @property
    def price(self):
        val = AESCipher.decrypt(self._price)
        return float(val) if val else 0.0

    @price.setter
    def price(self, value):
        self._price = AESCipher.encrypt(str(value))
