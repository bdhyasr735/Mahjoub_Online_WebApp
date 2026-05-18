# coding: utf-8
from datetime import datetime

# 🎯 الحل النهائي للـ Circular Import: الاستيراد المباشر لكائن db من النواة الأساسية للتطبيق
from apps import db

class Wallet(db.Model):
    """
    نموذج المحفظة المالية الموحد للموردين (Supplier Wallets).
    يدعم المنظومة الحسابية متعددة العملات بدقة متناهية (YER, SAR, USD).
    """
    __tablename__ = 'supplier_wallets'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # 🎯 التعديل الحاسم: تطابق تام مع معرف المورد النصي sovereign_id لاستقبال قيم مثل "SUP-MAH9631"
    supplier_id = db.Column(db.String(50), db.ForeignKey('suppliers.sovereign_id'), nullable=False, unique=True)
    wallet_code = db.Column(db.String(50), nullable=False, unique=True)
    
    # 💵 أرصدة الريال اليمني (تم ترقيتها إلى Numeric لضمان دقة العمليات المالية الحسابية)
    yer_total = db.Column(db.Numeric(15, 2), default=0.00, nullable=False)
    yer_withdrawn = db.Column(db.Numeric(15, 2), default=0.00, nullable=False)
    yer_pending = db.Column(db.Numeric(15, 2), default=0.00, nullable=False)

    # 🇸🇦 أرصدة الريال السعودي
    sar_total = db.Column(db.Numeric(15, 2), default=0.00, nullable=False)
    sar_withdrawn = db.Column(db.Numeric(15, 2), default=0.00, nullable=False)
    sar_pending = db.Column(db.Numeric(15, 2), default=0.00, nullable=False)

    # 🇱🇷 أرصدة الدولار الأمريكي
    usd_total = db.Column(db.Numeric(15, 2), default=0.00, nullable=False)
    usd_withdrawn = db.Column(db.Numeric(15, 2), default=0.00, nullable=False)
    usd_pending = db.Column(db.Numeric(15, 2), default=0.00, nullable=False)

    # 🗓️ الحالة والطوابع الزمنية (الحقل الذي كان مفقوداً في قاعدة البيانات)
    status = db.Column(db.String(20), default='نشطة', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # ─── الخصائص الحسابية (Properties) المحمية ───

    @property
    def yer_available(self):
        return max(0.00, float((self.yer_total or 0.00) - (self.yer_withdrawn or 0.00) - (self.yer_pending or 0.00)))

    @yer_available.setter
    def yer_available(self, value):
        pass

    @property
    def sar_available(self):
        return max(0.00, float((self.sar_total or 0.00) - (self.sar_withdrawn or 0.00) - (self.sar_pending or 0.00)))

    @sar_available.setter
    def sar_available(self, value):
        pass

    @property
    def usd_available(self):
        return max(0.00, float((self.usd_total or 0.00) - (self.usd_withdrawn or 0.00) - (self.usd_pending or 0.00)))

    @usd_available.setter
    def usd_available(self, value):
        pass

    def __init__(self, **kwargs):
        """تصفية تلقائية لمنع استثناء الـ no setter عند التأسيس السريع والتطابق التام مع الـ Properties."""
        computed_properties = {'yer_available', 'sar_available', 'usd_available'}
        filtered_kwargs = {k: v for k, v in kwargs.items() if k not in computed_properties}
        super(Wallet, self).__init__(**filtered_kwargs)

    def __repr__(self):
        return f"<Wallet {self.wallet_code}>"
