# coding: utf-8
# 📂 apps/models/statement_db.py

from apps.extensions import db
from datetime import datetime

class SupplierStatement(db.Model):
    """
    نموذج العمليات المحاسبية للموردين
    """
    __tablename__ = 'supplier_statements'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # الربط مع المورد (العلاقة هنا تتم عبر الـ ID مباشرة)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    
    # تفاصيل العملية
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(255), nullable=True) 
    
    # البيانات المالية
    currency = db.Column(db.String(10), default='USD') # USD, YER, SAR
    debit = db.Column(db.Float, default=0.0)    # مدين (ما عليك للمورد)
    credit = db.Column(db.Float, default=0.0)   # دائن (ما للمورد عندك)
    
    # الرصيد التراكمي
    running_balance = db.Column(db.Float, nullable=False)
    
    # ملاحظات
    notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<SupplierStatement {self.id} - Supplier ID: {self.supplier_id}>'
