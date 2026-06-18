# coding: utf-8
# 📂 apps/models/orders_db.py - النسخة النهائية الموحدة

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

    id = db.Column(db.String(100), primary_key=True)
    order_id = db.Column(db.String(50), nullable=False, index=True)
    
    # حقل السعر المخزن في قاعدة البيانات
    total_price_raw = db.Column('total_price', db.String(255), nullable=True)
    
    order_status = db.Column(db.String(30), default='pending', index=True)
    financial_status = db.Column(db.String(30), default='unpaid', index=True)
    fulfillment_status = db.Column(db.String(30), default='unfulfilled', index=True)
    
    customer_name = db.Column(db.String(150), nullable=True)
    shipping_city = db.Column(db.String(100), nullable=True)
    
    source = db.Column(db.String(50), default='QumraCloud')
    items_count = db.Column(db.Integer, default=1)
    created_at_local = db.Column(db.DateTime, default=datetime.utcnow)

    # الروابط
    items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def total_price(self):
        """فك تشفير السعر عند العرض فقط"""
        if not self.total_price_raw:
            return 0.0
        try:
            if cipher_suite:
                decrypted_data = cipher_suite.decrypt(self.total_price_raw.encode('utf-8'))
                return float(decrypted_data.decode('utf-8'))
            return float(self.total_price_raw)
        except Exception:
            return 0.0

    @total_price.setter
    def total_price(self, value):
        """تشفير السعر عند الحفظ"""
        if value is None:
            self.total_price_raw = None
            return
        try:
            str_val = str(float(value))
            if cipher_suite:
                self.total_price_raw = cipher_suite.encrypt(str_val.encode('utf-8')).decode('utf-8')
            else:
                self.total_price_raw = str_val
        except Exception as e:
            logger.error(f"❌ خطأ أثناء تشفير السعر: {e}")
            self.total_price_raw = str(value)

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.String(100), db.ForeignKey('processed_orders.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.String(100), nullable=False)
    product_name = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Float, default=0.0)
    sku = db.Column(db.String(100), nullable=True)
