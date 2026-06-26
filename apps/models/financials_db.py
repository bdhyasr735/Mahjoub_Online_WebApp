# coding: utf-8
# 📂 apps/models/financials_db.py

from datetime import datetime
from apps.extensions import db

class OrderFinancial(db.Model):
    __tablename__ = 'order_financials'

    # [صمام الأمان]: فهرسة مسمّاة ومنع تكرار التعريف لضمان الاستقرار
    __table_args__ = (
        db.Index('idx_fin_order_id', 'order_id'),
        db.Index('idx_fin_supplier_id', 'supplier_id'),
        db.Index('idx_fin_settlement', 'settlement_status'),
        db.Index('idx_fin_created', 'created_at'),
        {'extend_existing': True}
    )

    # 1. المعرفات والربط
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, unique=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    
    # 2. المبالغ المالية (معيار محاسبي دقيق)
    supplier_cost = db.Column(db.Numeric(18, 2), nullable=False)
    mahjoub_commission = db.Column(db.Numeric(18, 2), nullable=False)
    shipping_fees = db.Column(db.Numeric(18, 2), default=0.00)
    total_paid = db.Column(db.Numeric(18, 2), nullable=False)
    
    # 3. حالة التسوية
    settlement_status = db.Column(db.String(20), default='pending')
    
    # 4. توثيق زمني
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    settled_at = db.Column(db.DateTime, nullable=True)

    # [المسار الكامل]: الربط السيادي لمنع خطأ Multiple classes found
    order = db.relationship(
        'apps.models.orders_db.Order', 
        back_populates='financials'
    )
    supplier = db.relationship(
        'apps.models.supplier_db.Supplier', 
        back_populates='financials'
    )

    def calculate_net_profit(self):
        """دالة مساعدة لحساب الربح الصافي"""
        return self.mahjoub_commission

    def __repr__(self):
        return f'<OrderFinancial OrderID: {self.order_id} | Status: {self.settlement_status}>'
