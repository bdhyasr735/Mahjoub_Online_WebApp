# coding: utf-8
# 📂 apps/models/orders_db.py - إدارة وهيكلة بيانات الطلبات السيادية والتسويات المالية المشفرة

from apps.extensions import db
from datetime import datetime
from cryptography.fernet import Fernet
from config import Config
import logging

logger = logging.getLogger(__name__)

# تهيئة مفتاح التشفير الأمن المعتمد للمنصة لضمان سرية البيانات المالية والتجارية للطلب
try:
    # يفضل إعداد ENCRYPTION_KEY في ملف الكومفيج بشكل مستقر وثابت
    encryption_key = getattr(Config, 'ENCRYPTION_KEY', Fernet.generate_key().decode())
    cipher_suite = Fernet(encryption_key.encode())
except Exception as e:
    logger.error(f"⚠️ خطأ في تحميل مفتاح تشفير البيانات المالية: {e}")
    cipher_suite = None


class ProcessedOrder(db.Model):
    """النموذج المركزي الموحد لإدارة وتوثيق الطلبات المتزامنة والروابط المالية بالموردين"""
    __tablename__ = 'processed_orders'

    # المعرفات الأساسية
    id = db.Column(db.String(100), primary_key=True)  # المعرف الفريد القادم من API
    order_id = db.Column(db.String(50), nullable=False, index=True) # الرقم المرجعي للطلب
    
    # ربط المورد
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id', ondelete='SET NULL'), nullable=True)
    
    # الحالات
    order_status = db.Column(db.String(30), default='pending', index=True)
    financial_status = db.Column(db.String(30), default='unpaid', index=True)
    fulfillment_status = db.Column(db.String(30), default='unfulfilled', index=True)
    
    payment_type = db.Column(db.String(50), default='manual')
    
    # حقل السعر المشفر
    _total_price_encrypted = db.Column('total_price', db.String(255), nullable=True)
    
    # بيانات العميل
    customer_name = db.Column(db.String(150), nullable=True)
    customer_phone = db.Column(db.String(50), nullable=True)
    customer_email = db.Column(db.String(150), nullable=True)
    
    # بيانات الشحن
    shipping_country = db.Column(db.String(100), default='Yemen')
    shipping_city = db.Column(db.String(100), nullable=True)
    shipping_district = db.Column(db.String(100), nullable=True)
    shipping_street = db.Column(db.String(255), nullable=True)
    
    # حقول إضافية
    source = db.Column(db.String(50), default='QumraCloud')
    items_count = db.Column(db.Integer, default=1)
    
    # الطوابع الزمنية
    created_at_api = db.Column(db.DateTime, nullable=True)
    created_at_local = db.Column(db.DateTime, default=datetime.utcnow)

    # الروابط
    items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def total_price(self):
        """فك تشفير السعر عند العرض"""
        if not self._total_price_encrypted:
            return 0.0
        try:
            if cipher_suite:
                decrypted_data = cipher_suite.decrypt(self._total_price_encrypted.encode('utf-8'))
                return float(decrypted_data.decode('utf-8'))
            return float(self._total_price_encrypted)
        except Exception as e:
            logger.error(f"❌ خطأ فك تشفير السعر للطلب {self.id}: {e}")
            return 0.0

    @total_price.setter
    def total_price(self, value):
        """تشفير السعر عند الحفظ"""
        if value is None:
            self._total_price_encrypted = None
            return
        try:
            str_val = str(float(value))
            if cipher_suite:
                encrypted_data = cipher_suite.encrypt(str_val.encode('utf-8'))
                self._total_price_encrypted = encrypted_data.decode('utf-8')
            else:
                self._total_price_encrypted = str_val
        except Exception as e:
            logger.error(f"❌ خطأ أثناء تشفير السعر: {e}")
            self._total_price_encrypted = str(value)

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'total_price': self.total_price,
            'order_status': self.order_status,
            'customer': {'name': self.customer_name, 'phone': self.customer_phone},
            'shipping': {'city': self.shipping_city, 'street': self.shipping_street}
        }


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.String(100), db.ForeignKey('processed_orders.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.String(100), nullable=False)
    product_name = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Float, default=0.0)
    sku = db.Column(db.String(100), nullable=True)
