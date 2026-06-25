# coding: utf-8
# 📂 apps/models/financials_db.py

from apps.extensions import db
from datetime import datetime
from decimal import Decimal

class OrderFinancial(db.Model):
    __tablename__ = 'order_financials'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, unique=True, index=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False, index=True)
    
    # 1. المبالغ المالية (بمعيار دقيق)
    supplier_cost = db.Column(db.Numeric(15, 2), nullable=False) 
    mahjoub_commission = db.Column(db.Numeric(15, 2), nullable=False)
    shipping_fees = db.Column(db.Numeric(15, 2), default=0.00)
    total_paid = db.Column(db.Numeric(15, 2), nullable=False)
    
    # 2. حالة التسوية
    settlement_status = db.Column(db.String(20), default='pending', index=True) 
    
    # 3. توثيق زمني
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    settled_at = db.Column(db.DateTime, nullable=True)

    # 4. روابط الربط (باستخدام back_populates لضمان الاتساق مع الموديلات الأخرى)
    order = db.relationship('Order', back_populates='financials')
    supplier = db.relationship('Supplier', back_populates='financials')

    def calculate_net_profit(self):
        """دالة مساعدة لحساب الربح الصافي"""
        return self.mahjoub_commission

    def __repr__(self):
        return f'<OrderFinancial OrderID: {self.order_id} | Status: {self.settlement_status}>'
