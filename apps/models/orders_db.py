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
    cipher_suite = Fernet(getattr(Config, 'ENCRYPTION_KEY', Fernet.generate_key()))
except Exception as e:
    logger.error(f"⚠️ خطأ في تحميل مفتاح تشفير البيانات المالية: {e}")
    cipher_suite = None


class ProcessedOrder(db.Model):
    """النموذج المركزي الموحد لإدارة وتوثيق الطلبات المتزامنة والروابط المالية بالموردين"""
    __tablename__ = 'processed_orders'

    # المعرفات الأساسية للمزامنة والربط الجغرافي والسيادي لقمرة كلاود
    id = db.Column(db.String(100), primary_key=True)  # المعرف الفريد القادم من API (GraphQL ID)
    order_id = db.Column(db.String(50), nullable=False, index=True)  # الرقم المعروض أو المشتق للطلب
    
    # ربط وتوثيق المورد المحلي المسؤول عن تجهيز وتوفير الشحنة
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id', ondelete='SET NULL'), nullable=True)
    
    # الحالات الثلاثية المستقلة (حالة الطلب، الحالة المالية، حالة التجهيز والشحن)
    order_status = db.Column(db.String(30), default='pending', index=True)       # 'pending', 'confirmed', 'cancelled'
    financial_status = db.Column(db.String(30), default='unpaid', index=True)   # 'unpaid', 'paid', 'refunded'
    fulfillment_status = db.Column(db.String(30), default='unfulfilled', index=True) # 'unfulfilled', 'fulfilled'
    
    # نوع ووسيلة الدفع المتفق عليها
    payment_type = db.Column(db.String(50), default='manual')
    
    # حقل السعر الإجمالي المخزن مشفراً في قاعدة البيانات لحماية الخصوصية المالية
    _total_price_encrypted = db.Column('total_price', db.String(255), nullable=True)
    
    # بيانات العميل الأساسية للمشتري
    customer_name = db.Column(db.String(150), nullable=True)
    customer_phone = db.Column(db.String(50), nullable=True)
    customer_email = db.Column(db.String(150), nullable=True)
    
    # تفاصيل العنوان الجغرافي التفصيلي للشحن والتوصيل
    shipping_country = db.Column(db.String(100), default='Yemen')
    shipping_city = db.Column(db.String(100), nullable=True)
    shipping_district = db.Column(db.String(100), nullable=True)
    shipping_street = db.Column(db.String(255), nullable=True)
    
    # الطوابع الزمنية (توقيت النظام الخارجي وتوقيت التدوين المحلي)
    created_at_api = db.Column(db.DateTime, nullable=True)
    created_at_local = db.Column(db.DateTime, default=datetime.utcnow)

    # الروابط والعلاقات المباشرة
    items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def total_price(self):
        """فك تشفير السعر الإجمالي ديناميكياً عند استدعائه في لوحة التحكم وعرضه كقيمة عائمة"""
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
        """تشفير السعر الإجمالي تلقائياً قبل حفظه في قاعدة البيانات لحماية النزاهة المالية"""
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
            logger.error(f"❌ خطأ أثناء تشفير السعر الإجمالي للطلب: {e}")
            self._total_price_encrypted = str(value)

    def to_dict(self):
        """تحويل الكائن إلى قاموس تفصيلي آمن لاستخدامه في استجابات الـ API الداخلية للوحة التحكم"""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'supplier_id': self.supplier_id,
            'order_status': self.order_status,
            'financial_status': self.financial_status,
            'fulfillment_status': self.fulfillment_status,
            'payment_type': self.payment_type,
            'total_price': self.total_price,
            'customer': {
                'name': self.customer_name,
                'phone': self.customer_phone,
                'email': self.customer_email
            },
            'shipping': {
                'country': self.shipping_country,
                'city': self.shipping_city,
                'district': self.shipping_district,
                'street': self.shipping_street
            },
            'created_at_api': self.created_at_api.isoformat() if self.created_at_api else None,
            'created_at_local': self.created_at_local.isoformat()
        }


class OrderItem(db.Model):
    """توثيق وحفظ العناصر والمنتجات الفردية المكونة للطلب السيادي المعالج"""
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.String(100), db.ForeignKey('processed_orders.id', ondelete='CASCADE'), nullable=False)
    
    # تفاصيل المنتج القادم من واجهة التزامن
    product_id = db.Column(db.String(100), nullable=False)
    product_name = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    
    # سعر القطعة الفردية (حفظ تقليدي أو مشفر حسب الرغبة، مفضل حفظه لتسهيل الجرد)
    unit_price = db.Column(db.Float, default=0.0)
    sku = db.Column(db.String(100), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'sku': self.sku
        }
