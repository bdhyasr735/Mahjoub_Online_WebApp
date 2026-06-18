# coding: utf-8
# 📂 apps/models/orders_db.py - نموذج الطلبات التفصيلي والمشفر (النسخة النهائية المستقرة المتوافقة مع قمرة كلاود 2026)

import base64
import hashlib
import logging
from datetime import datetime
from decimal import Decimal
from cryptography.fernet import Fernet
from apps.extensions import db
from config import Config

logger = logging.getLogger(__name__)

# 1. إعداد محرك التشفير الآمن لبيانات الأسعار الحساسة
try:
    raw_key = Config.ENCRYPTION_KEY
    hashed_key = hashlib.sha256(raw_key.encode()).digest()
    fernet_key = base64.urlsafe_b64encode(hashed_key)
    cipher_suite = Fernet(fernet_key)
except Exception as e:
    logger.critical(f"❌ [Critical] فشل إعداد محرك التشفير: {e}")
    raise e

class ProcessedOrder(db.Model):
    __tablename__ = 'processed_orders'

    # البيانات الأساسية المعرفية للطلب (مثل المعرف الفريد الداخلي والمعرف الظاهري من قمرة)
    id = db.Column(db.String(100), primary_key=True)  # يستوعب الـ GraphQL UUID أو الـ id
    order_id = db.Column(db.String(100), nullable=True, index=True)  # الـ الرقم الظاهري مثل "1000000943"
    
    # 🧭 الحالات الثلاث الثلاثية المستقلة المعتمدة رسمياً في قمرة
    order_status = db.Column(db.String(50), default='pending')        # [pending, confirmed, cancelled, delivered, returned, refunded]
    financial_status = db.Column(db.String(50), default='unpaid')    # [unpaid, paid, pending, refunded]
    fulfillment_status = db.Column(db.String(50), default='unfulfilled') # [unfulfilled, fulfilled, partial]
    
    # حقول تفصيلية لبيانات العميل والشحن الصريحة المستلمة
    customer_name = db.Column(db.String(255), nullable=True)
    customer_phone = db.Column(db.String(50), nullable=True)
    customer_email = db.Column(db.String(255), nullable=True)
    
    # حقول العنوان الجغرافي المستخرجة من هيكل العنوان لقمرة
    shipping_country = db.Column(db.String(100), nullable=True)
    shipping_city = db.Column(db.String(100), nullable=True)
    shipping_district = db.Column(db.String(100), nullable=True)
    shipping_street = db.Column(db.Text, nullable=True)
    
    # بيانات وسيلة الدفع والحمل
    payment_type = db.Column(db.String(50), default='manual')  # [manual, cod]
    items_count = db.Column(db.Integer, default=0)
    source = db.Column(db.String(100), default='QumraCloud')
    
    # 🔗 مفتاح الربط والتحكم الخاص بـ المورد المحلي (خيارات الـ AJAX باللوحة)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=True)
    
    # التواريخ والمزامنة زمنياً (معالجة UTC)
    created_at_api = db.Column(db.DateTime, nullable=True)  
    processed_at = db.Column(db.DateTime, default=datetime.utcnow)  
    
    # الحقل المشفر للقيمة المالية الإجمالية (لحماية البيانات الحساسة للمنصة)
    _encrypted_total_price = db.Column(db.Text, nullable=True)

    # العلاقة المباشرة لقراءة بيانات المورد مع الكود المحلي
    supplier = db.relationship('Supplier', backref=db.backref('processed_orders', lazy='dynamic'))

    # 2. إدارة التشفير والتعمية المالية (Property Getters/Setters)
    @property
    def total_price(self):
        """فك تشفير السعر آلياً عند الاستدعاء من اللوحة والقراءة برمجياً"""
        if not self._encrypted_total_price:
            return Decimal('0.0')
        try:
            decrypted_val = cipher_suite.decrypt(self._encrypted_total_price.encode()).decode()
            return Decimal(decrypted_val)
        except Exception as e:
            logger.error(f"⚠️ خطأ أثناء فك تشفير السعر للطلب {self.id}: {e}")
            return Decimal('0.0')

    @total_price.setter
    def total_price(self, value):
        """تشفير السعر بطبقة AES-256 قبل الحفظ الفعلي في قاعدة البيانات اللامركزية"""
        try:
            val_to_encrypt = str(value) if value is not None else '0.0'
            self._encrypted_total_price = cipher_suite.encrypt(val_to_encrypt.encode()).decode()
        except Exception as e:
            logger.error(f"❌ خطأ أثناء تشفير السعر للطلب {self.id}: {e}")
            raise ValueError("فشل تشفير القيمة المالية")

    def __repr__(self):
        return f"<ProcessedOrder ID: {self.id} | OrderNo: {self.order_id} | Status: {self.order_status}>"


# 3. جدول تفاصيل محتويات الطلب المترابط (Order Items)
class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(100), db.ForeignKey('processed_orders.id'), nullable=False)
    product_name = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Numeric(10, 2), default=0.0)
    
    # علاقة الربط الوثيقة مع الطلب الرئيسي والـ Cascade للحذف والتعديل المترابط
    order = db.relationship(
        'ProcessedOrder', 
        backref=db.backref('items', lazy='dynamic', cascade="all, delete-orphan")
    )

    def __repr__(self):
        return f"<OrderItem {self.product_name} - Qty: {self.quantity}>"
