# coding: utf-8
from apps import db
from datetime import datetime

class VendorWallet(db.Model):
    __tablename__ = 'vendor_wallets'

    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False, unique=True, index=True)
    
    # 1. الأرصدة (محسوبة بدقة)
    # نستخدم Numeric للتعامل مع العملات بدقة (15 خانة إجمالي، 2 خانة عشرية)
    balance_available = db.Column(db.Numeric(15, 2), default=0.00) # متاح للسحب
    balance_pending = db.Column(db.Numeric(15, 2), default=0.00)   # مبالغ تحت التسوية
    total_withdrawn = db.Column(db.Numeric(15, 2), default=0.00)   # إجمالي المسحوبات
    
    # 2. الفهرسة للأداء السريع (للتقارير المالية)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    
    # 3. الربط
    supplier = db.relationship('Supplier', backref=db.backref('wallet', uselist=False))

    def __repr__(self):
        return f'<Wallet SupplierID: {self.supplier_id} | Balance: {self.balance_available}>'
