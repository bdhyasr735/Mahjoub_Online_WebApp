# coding: utf-8
# 📂 apps/models/financials_db.py

import os
from datetime import datetime
from cryptography.fernet import Fernet
from apps.extensions import db

class OrderFinancial(db.Model):
    """المركز المالي للطلبات: المحرك المحاسبي للمنصة والموردين."""
    __tablename__ = 'order_financials'

    # [فهرسة الأداء]: تحسين سرعة الاستعلامات والربط المالي
    __table_args__ = (
        db.Index('idx_fin_order_id', 'order_id'),
        db.Index('idx_fin_supplier_id', 'supplier_id'),
        db.Index('idx_fin_settlement', 'settlement_status'),
        db.Index('idx_fin_created', 'created_at'),
        db.Index('idx_fin_transaction', 'transaction_id'),
        {'extend_existing': True}
    )

    # 1. المعرفات والربط
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(100), db.ForeignKey('orders.id'), nullable=False, unique=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    transaction_id = db.Column(db.Integer, db.ForeignKey('wallet_transactions.id'), nullable=True)
    
    # 2. المبالغ المالية (تشفير محكم + قيمة خام للعمليات الحسابية السريعة)
    _supplier_cost_enc = db.Column(db.String(255), nullable=False)
    supplier_cost_raw = db.Column(db.Numeric(18, 2), default=0.00)
    
    _mahjoub_commission_enc = db.Column(db.String(255), nullable=False)
    mahjoub_commission_raw = db.Column(db.Numeric(18, 2), default=0.00)
    
    _total_paid_enc = db.Column(db.String(255), nullable=False)
    total_paid_raw = db.Column(db.Numeric(18, 2), default=0.00)
    
    shipping_fees = db.Column(db.Numeric(18, 2), default=0.00)
    
    # 3. حالة التسوية
    settlement_status = db.Column(db.String(20), default='pending') 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    settled_at = db.Column(db.DateTime, nullable=True)

    # [التحميل المتصل]: استخدام joined لضمان جلب بيانات Order و Supplier فوراً
    order = db.relationship('Order', back_populates='financials', lazy='joined')
    supplier = db.relationship('Supplier', back_populates='financials', lazy='joined')
    transaction = db.relationship('WalletTransaction', backref='order_financials', lazy='joined')

    def __init__(self, **kwargs):
        """مُنشئ الكائن مع التشفير التلقائي للمبالغ عند الإنشاء."""
        supplier_cost_val = kwargs.pop('supplier_cost', None)
        commission_val = kwargs.pop('mahjoub_commission', None)
        total_paid_val = kwargs.pop('total_paid', None)

        super().__init__(**kwargs)

        if supplier_cost_val is not None:
            self.supplier_cost = supplier_cost_val
        elif not self._supplier_cost_enc:
            self._supplier_cost_enc = self._encrypt(self.supplier_cost_raw or 0.0)

        if commission_val is not None:
            self.mahjoub_commission = commission_val
        elif not self._mahjoub_commission_enc:
            self._mahjoub_commission_enc = self._encrypt(self.mahjoub_commission_raw or 0.0)

        if total_paid_val is not None:
            self.total_paid = total_paid_val
        elif not self._total_paid_enc:
            self._total_paid_enc = self._encrypt(self.total_paid_raw or 0.0)

    # --- منطق التشفير السيادي ---
    @staticmethod
    def _get_key():
        key = os.environ.get('ENCRYPTION_KEY')
        return key.encode() if key else b'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8Vq='

    def _encrypt(self, value):
        if value is None:
            value = 0.0
        f = Fernet(self._get_key())
        return f.encrypt(str(value).encode()).decode()

    def _decrypt(self, value):
        if not value:
            return 0.0
        try:
            f = Fernet(self._get_key())
            return float(f.decrypt(value.encode()).decode())
        except Exception:
            return 0.0

    # --- Properties الذكية للتعامل مع البيانات ---
    @property
    def supplier_cost(self):
        val = self._decrypt(self._supplier_cost_enc)
        return val if val != 0.0 else float(self.supplier_cost_raw or 0.0)

    @supplier_cost.setter
    def supplier_cost(self, value):
        val_float = float(value or 0.0)
        self._supplier_cost_enc = self._encrypt(val_float)
        self.supplier_cost_raw = val_float

    @property
    def mahjoub_commission(self):
        val = self._decrypt(self._mahjoub_commission_enc)
        return val if val != 0.0 else float(self.mahjoub_commission_raw or 0.0)

    @mahjoub_commission.setter
    def mahjoub_commission(self, value):
        val_float = float(value or 0.0)
        self._mahjoub_commission_enc = self._encrypt(val_float)
        self.mahjoub_commission_raw = val_float

    @property
    def total_paid(self):
        val = self._decrypt(self._total_paid_enc)
        return val if val != 0.0 else float(self.total_paid_raw or 0.0)

    @total_paid.setter
    def total_paid(self, value):
        val_float = float(value or 0.0)
        self._total_paid_enc = self._encrypt(val_float)
        self.total_paid_raw = val_float

    # =========================================================
    # 📌 قواعد "المورد له سعر التكلفة فقط" والخصائص التوافقية
    # =========================================================

    @property
    def supplier_payout(self):
        """مستحقات المورد الخالصة = سعر التكلفة فقط."""
        return self.supplier_cost

    @property
    def supplier_share(self):
        """حصة المورد المحاسبية = سعر التكلفة فقط."""
        return self.supplier_cost

    @property
    def supplier_amount(self):
        """مرادف لحصة المورد للتوافق مع التمبلت."""
        return self.supplier_cost

    @property
    def platform_profit(self):
        """صافي ربح المنصة = إجمالي المدفوع - تكلفة المورد - رسوم الشحن."""
        return float(self.total_paid or 0.0) - float(self.supplier_cost or 0.0) - float(self.shipping_fees or 0.0)

    @property
    def currency(self):
        """العملة ثابتة: ريال سعودي (SAR)"""
        return "SAR"

    def __repr__(self):
        return f'<OrderFinancial OrderID: {self.order_id} | SupplierCost: {self.supplier_cost} SAR | Status: {self.settlement_status}>'
