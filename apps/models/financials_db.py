# coding: utf-8
from apps import db
from datetime import datetime
from decimal import Decimal

class OrderFinancial(db.Model):
    __tablename__ = 'order_financials'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, unique=True, index=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False, index=True)
    
    # 1. المبالغ المالية (بمعيار دقيق)
    # تكلفة المنتج الأصلية من المورد
    supplier_cost = db.Column(db.Numeric(15, 2), nullable=False) 
    # عمولة المنصة (ربحنا الصافي)
    mahjoub_commission = db.Column(db.Numeric(15, 2), nullable=False)
    # تكلفة الشحن المحصلة
    shipping_fees = db.Column(db.Numeric(15, 2), default=0.00)
    # إجمالي المبلغ الذي دفعه العميل
    total_paid = db.Column(db.Numeric(15, 2), nullable=False)
    
    # 2. حالة التسوية (للمرحلة الثانية - الأتمتة)
    settlement_status = db.Column(db.String(20), default='pending', index=True) # pending, settled
    
    # 3. توثيق زمني
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    settled_at = db.Column(db.DateTime, nullable=True) # تاريخ التحويل للمورد

    # روابط الربط
    order = db.relationship('Order', backref=db.backref('financials', uselist=False))
    supplier = db.relationship('Supplier', backref='financials')

    def __repr__(self):
        return f'<Financial OrderID: {self.order_id} | Status: {self.settlement_status}>'
