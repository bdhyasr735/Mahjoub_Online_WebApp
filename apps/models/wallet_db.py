# coding: utf-8
from datetime import datetime
from apps import db

class Wallet(db.Model):
    """
    نموذج المحفظة المالية الموحد للموردين (Supplier Wallets).
    يدعم المنظومة الحسابية متعددة العملات (YER, SAR, USD).
    """
    __tablename__ = 'supplier_wallets'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # 🎯 التعديل الحاسم: تحويل الحقل إلى String(50) ليتطابق مع sovereign_id النصي للموردين ويقبل "SUP-MAH9631"
    supplier_id = db.Column(db.String(50), db.ForeignKey('suppliers.sovereign_id'), nullable=False, unique=True)
    wallet_code = db.Column(db.String(50), nullable=False, unique=True)
    
    # 💵 أرصدة الريال اليمني الحقيقية
    yer_total = db.Column(db.Float, default=0.0, nullable=False)
    yer_withdrawn = db.Column(db.Float, default=0.0, nullable=False)
    yer_pending = db.Column(db.Float, default=0.0, nullable=False)

    # 🇸🇦 أرصدة الريال السعودي الحقيقية
    sar_total = db.Column(db.Float, default=0.0, nullable=False)
    sar_withdrawn = db.Column(db.Float, default=0.0, nullable=False)
    sar_pending = db.Column(db.Float, default=0.0, nullable=False)

    # 🇱🇷 أرصدة الدولار الأمريكي الحقيقية
    usd_total = db.Column(db.Float, default=0.0, nullable=False)
    usd_withdrawn = db.Column(db.Float, default=0.0, nullable=False)
    usd_pending = db.Column(db.Float, default=0.0, nullable=False)

    # 🗓️ الحالة والطوابع الزمنية
    status = db.Column(db.String(20), default='نشطة', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # ─── الخصائص الحسابية (Properties) المحمية ───

    @property
    def yer_available(self):
        return max(0.0, (self.yer_total or 0.0) - (self.yer_withdrawn or 0.0) - (self.yer_pending or 0.0))

    @yer_available.setter
    def yer_available(self, value):
        pass

    @property
    def sar_available(self):
        return max(0.0, (self.sar_total or 0.0) - (self.sar_withdrawn or 0.0) - (self.sar_pending or 0.0))

    @sar_available.setter
    def sar_available(self, value):
        pass

    @property
    def usd_available(self):
        return max(0.0, (self.usd_total or 0.0) - (self.usd_withdrawn or 0.0) - (self.usd_pending or 0.0))

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
