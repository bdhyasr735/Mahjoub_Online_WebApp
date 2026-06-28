# coding: utf-8
# 📂 apps/models/orders_db.py

from datetime import datetime
from cryptography.fernet import Fernet
from apps.extensions import db
import os

# تهيئة مفتاح التشفير
cipher = Fernet(os.getenv('ENCRYPTION_KEY', Fernet.generate_key()))

class Order(db.Model):
    __tablename__ = 'orders'

    # [صمام الأمان]: الفهارس لا تعمل على الأعمدة المشفرة، لذا نركز على أعمدة البحث والربط
    __table_args__ = (
        db.Index('idx_ord_supplier_id', 'supplier_id'),
        db.Index('idx_ord_ref', 'order_reference'),
        db.Index('idx_ord_status', 'status'),
        db.Index('idx_ord_created', 'created_at'),
        {'extend_existing': True}
    )

    # 1. المعرف (استخدمنا String ليتوافق مع _id الخاص بـ API قمرة)
    id = db.Column(db.String(100), primary_key=True)
    
    # 2. البيانات المالية والربط
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=True)
    order_reference = db.Column(db.String(100), unique=True, nullable=True) 
    
    # حقول المزامنة الجديدة (لا تشفرها لأننا نحتاج للبحث والفرز بها)
    total_price = db.Column(db.Float, default=0.0)
    items_count = db.Column(db.Integer, default=0)
    
    # 3. بيانات الشحن (مشفرة)
    _customer_name = db.Column('customer_name', db.Text)
    _customer_phone = db.Column('customer_phone', db.Text)
    customer_address = db.Column(db.Text) 
    
    # 4. حالة الطلب
    status = db.Column(db.String(30), default='pending') 
    
    # 5. التوثيق الزمني
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 6. العلاقات
    supplier = db.relationship('Supplier', back_populates='orders')
    financials = db.relationship('OrderFinancial', back_populates='order', uselist=False, cascade="all, delete-orphan")

    # --- منطق التشفير (لا يؤثر على الأداء، فقط عند القراءة والكتابة) ---
    @property
    def customer_name(self):
        try:
            return cipher.decrypt(self._customer_name.encode()).decode()
        except: return "غير معروف"

    @customer_name.setter
    def customer_name(self, value):
        self._customer_name = cipher.encrypt(value.encode()).decode()

    @property
    def customer_phone(self):
        try:
            return cipher.decrypt(self._customer_phone.encode()).decode()
        except: return "غير متوفر"

    @customer_phone.setter
    def customer_phone(self, value):
        self._customer_phone = cipher.encrypt(value.encode()).decode()

    def __repr__(self):
        return f'<Order {self.id} | Status: {self.status}>'
