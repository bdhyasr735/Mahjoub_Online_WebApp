from datetime import datetime
from apps import db

class Wallet(db.Model):
    """
    نموذج المحفظة المالية الموحد والسيادي للموردين (Supplier Wallets).
    يدعم المنظومة الحسابية متعددة العملات (YER, SAR, USD).
    """
    __tablename__ = 'supplier_wallets'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    supplier_id = db.Column(db.String(50), db.ForeignKey('suppliers.sovereign_id'), nullable=False, unique=True)
    wallet_code = db.Column(db.String(50), nullable=False, unique=True)
    
    # 💵 أعمدة رصيد الريال اليمني (الأعمدة الحقيقية في قاعدة البيانات)
    yer_total = db.Column(db.Float, default=0.0, nullable=False)
    yer_withdrawn = db.Column(db.Float, default=0.0, nullable=False)
    yer_pending = db.Column(db.Float, default=0.0, nullable=False)

    # 🇸🇦 أعمدة رصيد الريال السعودي (الأعمدة الحقيقية في قاعدة البيانات)
    sar_total = db.Column(db.Float, default=0.0, nullable=False)
    sar_withdrawn = db.Column(db.Float, default=0.0, nullable=False)
    sar_pending = db.Column(db.Float, default=0.0, nullable=False)

    # 🇱🇷 أعمدة رصيد الدولار الأمريكي (الأعمدة الحقيقية في قاعدة البيانات)
    usd_total = db.Column(db.Float, default=0.0, nullable=False)
    usd_withdrawn = db.Column(db.Float, default=0.0, nullable=False)
    usd_pending = db.Column(db.Float, default=0.0, nullable=False)

    # 🗓️ الطوابع الزمنية والحالة الحوكمة
    status = db.Column(db.String(20), default='نشطة', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # ─── الخصائص الديناميكية المتقدمة (Properties) مع توفير الـ Setters لمنع خطأ الـ 500 ───

    @property
    def yer_available(self):
        """حساب الرصيد المتاح بالريال اليمني تلقائياً."""
        return max(0.0, (self.yer_total or 0.0) - (self.yer_withdrawn or 0.0) - (self.yer_pending or 0.0))

    @yer_available.setter
    def yer_available(self, value):
        """مستقبل القيمة الآمن لحماية الكائن أثناء الإنشاء التلقائي."""
        pass

    @property
    def sar_available(self):
        """حساب الرصيد المتاح بالريال السعودي تلقائياً."""
        return max(0.0, (self.sar_total or 0.0) - (self.sar_withdrawn or 0.0) - (self.sar_pending or 0.0))

    @sar_available.setter
    def sar_available(self, value):
        """مستقبل القيمة الآمن لحماية الكائن أثناء الإنشاء التلقائي."""
        pass

    @property
    def usd_available(self):
        """حساب الرصيد المتاح بالدولار الأمريكي تلقائياً."""
        return max(0.0, (self.usd_total or 0.0) - (self.usd_withdrawn or 0.0) - (self.usd_pending or 0.0))

    @usd_available.setter
    def usd_available(self, value):
        """مستقبل القيمة الآمن لحماية الكائن أثناء الإنشاء التلقائي."""
        pass

    def __init__(self, **kwargs):
        """
        منشئ الكائن المطور لتنظيف ومعالجة المعاملات البرمجية وتجاهل الخصائص المقروءة 
        فقط تلقائياً أثناء تشغيل استعلامات SQLAlchemy.
        """
        # عزل الخصائص الحسابية لمنع تلوث حقول قاعدة البيانات أثناء الـ Insertion
        computed_properties = {'yer_available', 'sar_available', 'usd_available'}
        filtered_kwargs = {k: v for k, v in kwargs.items() if k not in computed_properties}
        
        super(Wallet, self).__init__(**filtered_kwargs)

    def __repr__(self):
        return f"<Wallet {self.wallet_code} - Supplier {self.supplier_id}>"
