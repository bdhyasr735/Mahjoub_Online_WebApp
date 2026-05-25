# coding: utf-8
# 🏦 نموذج تسويات الموردين - منصة محجوب أونلاين 2026
from datetime import datetime
from apps.extensions import db

class AdminSettlement(db.Model):
    __tablename__ = 'admin_settlements'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False, index=True)
    
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    settlement_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    payment_method = db.Column(db.String(50), nullable=True) # تحويل، نقدي، إلخ
    reference_number = db.Column(db.String(100), nullable=True) # رقم سند التحويل
    notes = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f"<AdminSettlement {self.id} | Supplier: {self.supplier_id} | {self.amount} {self.currency}>"
