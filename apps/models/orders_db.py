# coding: utf-8
from apps import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    
    # 1. روابط السيادة والتبعية
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False, index=True)
    order_reference = db.Column(db.String(100), unique=True, nullable=False, index=True) # رقم الطلب الفريد
    
    # 2. بيانات الشحن اللوجستية (للزبون)
    customer_name = db.Column(db.String(150), index=True)
    customer_phone = db.Column(db.String(20), index=True)
    customer_address = db.Column(db.Text) # محافظة، مديرية، حي
    
    # 3. حالة الطلب (مفهرسة لتتبع التقدم)
    status = db.Column(db.String(30), default='pending', index=True) # pending, processing, shipped, delivered, cancelled
    
    # 4. التوثيق الزمني الدقيق
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)

    # 5. الربط مع المورد
    supplier = db.relationship('Supplier', backref='orders')

    def __repr__(self):
        return f'<Order {self.order_reference} | Status: {self.status}>'
