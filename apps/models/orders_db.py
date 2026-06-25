# coding: utf-8
# 📂 apps/models/orders_db.py

from apps.extensions import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'orders'

    # 1. المعرف الأساسي
    id = db.Column(db.Integer, primary_key=True)
    
    # 2. روابط السيادة (مع Index للبحث السريع)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False, index=True)
    order_reference = db.Column(db.String(100), unique=True, nullable=False, index=True) # رقم الطلب الفريد
    
    # 3. بيانات الشحن اللوجستية (للزبون)
    customer_name = db.Column(db.String(150), index=True)
    customer_phone = db.Column(db.String(20), index=True)
    customer_address = db.Column(db.Text) 
    
    # 4. حالة الطلب (مفهرسة لتتبع التقدم)
    status = db.Column(db.String(30), default='pending', index=True) 
    
    # 5. التوثيق الزمني الدقيق (مع Index لعمليات الفرز والتقارير)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)

    # 6. العلاقات (Relationships)
    # الربط مع المورد
    supplier = db.relationship('Supplier', back_populates='orders')
    
    # الربط مع المالية (One-to-One)
    financials = db.relationship('OrderFinancial', back_populates='order', uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Order {self.order_reference} | Status: {self.status}>'
