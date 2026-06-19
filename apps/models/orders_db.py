# coding: utf-8
# 📂 apps/models/orders_db.py - النسخة النهائية المحدثة (الدستور البرمجي)

from apps.extensions import db
from datetime import datetime
from cryptography.fernet import Fernet
from config import Config
import logging

logger = logging.getLogger(__name__)

# تهيئة مفتاح التشفير
try:
    encryption_key = getattr(Config, 'ENCRYPTION_KEY', Fernet.generate_key().decode())
    cipher_suite = Fernet(encryption_key.encode())
except Exception as e:
    logger.error(f"⚠️ خطأ في تحميل مفتاح تشفير البيانات: {e}")
    cipher_suite = None

class ProcessedOrder(db.Model):
    __tablename__ = 'processed_orders'

    # 1. البيانات العامة والتعريفية
    id = db.Column(db.String(100), primary_key=True) # المعرف التقني
    order_id = db.Column(db.String(50), nullable=False, index=True) # رقم الطلب #...
    order_status = db.Column(db.String(30), default='pending', index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)

    # 2. بيانات العميل
    customer_name = db.Column(db.String(150), nullable=True)
    customer_phone = db.Column(db.String(50), nullable=True)
    customer_phone2 = db.Column(db.String(50), nullable=True)
    customer_email = db.Column(db.String(100), nullable=True)
    customer_source = db.Column(db.String(50), nullable=True)
    customer_type = db.Column(db.String(30), default='guest') # guest/registered

    # 3. بيانات الشحن
    shipping_city = db.Column(db.String(100), nullable=True)
    shipping_country = db.Column(db.String(100), nullable=True)
    shipping_district = db.Column(db.String(100), nullable=True)
    shipping_street = db.Column(db.String(255), nullable=True)
    shipping_price = db.Column(db.Float, default=0.0)
    fulfillment_status = db.Column(db.String(30), default='unfulfilled', index=True)
    channel = db.Column(db.String(50), default='STORE')

    # 4. البيانات المالية
    # تشفير السعر لضمان الخصوصية
    total_price_raw = db.Column('total_price', db.String(255), nullable=True)
    sub_total = db.Column(db.Float, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)
    financial_status = db.Column(db.String(30), default='unpaid', index=True)
    payment_type = db.Column(db.String(50), default='manual')
    paid_at = db.Column(db.DateTime, nullable=True)
    currency = db.Column(db.String(10), default='SAR')

    items_count = db.Column(db.Integer, default=0)
    items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def total_price(self):
        if not self.total_price_raw: return 0.0
        try:
            if cipher_suite:
                return float(cipher_suite.decrypt(self.total_price_raw.encode()).decode())
            return float(self.total_price_raw)
        except: return 0.0

    @total_price.setter
    def total_price(self, value):
        val = str(float(value or 0))
        self.total_price_raw = cipher_suite.encrypt(val.encode()).decode() if cipher_suite else val

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.String(100), db.ForeignKey('processed_orders.id', ondelete='CASCADE'), nullable=False)
    
    product_title = db.Column(db.String(255), nullable=False)
    sku = db.Column(db.String(100), nullable=True)
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float, default=0.0) # سعر الوحدة
    total_price = db.Column(db.Float, default=0.0) # السعر الإجمالي للصنف
    compare_at_price = db.Column(db.Float, default=0.0)
    total_savings = db.Column(db.Float, default=0.0)
    product_image = db.Column(db.String(500), nullable=True)
