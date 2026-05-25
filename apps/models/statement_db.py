# coding: utf-8
# 📊 نموذج كشوفات الحسابات الموحد - نظام محجوب أونلاين 2026
# هذا الجدول مخصص لأرشفة كافة العمليات المالية وربطها برصيد تراكمي دقيق

from datetime import datetime
from apps.extensions import db

class SupplierStatement(db.Model):
    """ 
    جدول كشف الحساب التاريخي للمورد (Ledger) 
    يقوم بأرشفة العمليات المالية لضمان الشفافية والمراجعة
    """
    __tablename__ = 'supplier_statements'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('supplier_wallets.id'), nullable=False)
    
    # 🕒 تفاصيل التوقيت والوصف
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    description = db.Column(db.String(255), nullable=False) # وصف العملية (مثال: إيداع مبيعات، سحب نقدي)
    currency = db.Column(db.String(10), nullable=False)    # YER, SAR, USD
    
    # 🧮 القيم المالية (نظام القيد المزدوج المبسط)
    # debit: يمثل خصم من رصيد المورد (سحب)
    # credit: يمثل إضافة لرصيد المورد (مبيعات/إيداع)
    debit = db.Column(db.Numeric(15, 2), default=0.00)  
    credit = db.Column(db.Numeric(15, 2), default=0.00) 
    
    # الرصيد التراكمي (يتم تحديثه لحظة تسجيل العملية)
    running_balance = db.Column(db.Numeric(15, 2), nullable=False) 
    
    # 🔗 الربط المرجعي (للوصول للعملية الأصلية للتدقيق)
    reference_type = db.Column(db.String(50)) # 'TRANSACTION' أو 'SETTLEMENT'
    reference_id = db.Column(db.Integer)      # معرف السجل في الجدول الأصلي

    def __repr__(self):
        return f"<SupplierStatement {self.id} | Balance: {self.running_balance} {self.currency}>"
