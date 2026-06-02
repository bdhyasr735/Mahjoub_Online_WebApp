# coding: utf-8
# 📂 apps/models/wallet_db.py - نموذج المحفظة والعمليات المالية

from apps.extensions import db
from datetime import datetime

class SupplierWallet(db.Model):
    """جدول أرصدة الموردين"""
    __tablename__ = 'supplier_wallets'
    
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    wallet_code = db.Column(db.String(50), unique=True, nullable=False)
    sar_total = db.Column(db.Float, default=0.0)
    yer_total = db.Column(db.Float, default=0.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقة مع المورد
    supplier = db.relationship('Supplier', backref='wallet')

    def __repr__(self):
        return f'<Wallet {self.wallet_code}>'

class WalletTransaction(db.Model):
    """جدول سجل العمليات المالية (سحب/إيداع/تحويل)"""
    __tablename__ = 'wallet_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('supplier_wallets.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False) # 'سحب', 'إيداع'
    status = db.Column(db.String(20), default='قيد الانتظار') # 'قيد الانتظار', 'ناجحة', 'مرفوضة'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقة مع المحفظة
    wallet = db.relationship('SupplierWallet', backref='transactions')

    def __repr__(self):
        return f'<Transaction {self.id} - {self.status}>'
