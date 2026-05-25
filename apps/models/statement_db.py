# coding: utf-8
# 📂 apps/models/statement_db.py
from apps.extensions import db
from datetime import datetime

class SupplierStatement(db.Model):
    __tablename__ = 'supplier_statements'
    
    id = db.Column(db.Integer, primary_key=True)
    # الربط مع المورد
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    
    # تفاصيل العملية المحاسبية
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reference_number = db.Column(db.String(50), nullable=True)  # رقم الفاتورة أو السند
    description = db.Column(db.String(255), nullable=True)     # بيان الحركة
    
    # العملة
    currency = db.Column(db.String(10), default='USD') # USD, YER, SAR
    
    # الجانب المحاسبي (دائن/مدين)
    # إذا كان المبلغ إيجابياً فهو دائن (Credit)، وإذا كان سالباً فهو مدين (Debit)
    debit = db.Column(db.Float, default=0.0)    # مدين (ما عليك للمورد)
    credit = db.Column(db.Float, default=0.0)   # دائن (ما للمورد عندك)
    
    # الرصيد التراكمي بعد هذه الحركة
    running_balance = db.Column(db.Float, nullable=False)
    
    # ملاحظات إضافية
    notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<SupplierStatement {self.id} - Supplier: {self.supplier_id}>'
