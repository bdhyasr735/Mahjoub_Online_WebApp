from core import db
from datetime import datetime
from flask_login import UserMixin

class Supplier(db.Model, UserMixin):
    """
    موديل المورد السيادي - نظام محجوب أونلاين MAH-9046
    يجمع بين الهوية الرقمية، الحوكمة المالية، والربط بالمخزون التيهامي.
    """
    __tablename__ = 'supplier'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # --- بيانات الدخول والتعميد ---
    # ملاحظة: يتم استخدام 'name' كمعرف أساسي في عملية تسجيل الدخول
    name = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    activity_type = db.Column(db.String(100))
    
    # --- 🛡️ نظام الرقابة والاعتماد السيادي ---
    # الحقل المحوري الذي يتحكم في ظهور الداشبورد أو صفحة الانتظار
    is_approved = db.Column(db.Boolean, default=False) 
    status = db.Column(db.String(20), default='pending') # pending, active, suspended
    
    # --- تفاصيل المنشأة الجغرافية ---
    trade_name = db.Column(db.String(200))
    full_name = db.Column(db.String(200))
    province = db.Column(db.String(100)) # المحافظة (مثل: الحديدة)
    district = db.Column(db.String(100)) # المديرية (مثل: الخوخة)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True, nullable=False)

    # --- 💰 النظام المالي المتعدد (Multicurrency Wallet) ---
    wallet_balance = db.Column(db.Float, default=0.0) # الرصيد المرجعي الإجمالي
    wallet_usd = db.Column(db.Float, default=0.0)     # العملة الصعبة
    wallet_sar = db.Column(db.Float, default=0.0)     # الريال السعودي
    wallet_yer = db.Column(db.Float, default=0.0)     # الريال اليمني
    
    bank_name = db.Column(db.String(100))
    bank_acc = db.Column(db.String(100))
    fin_type = db.Column(db.String(50))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # --- 📦 علاقة الربط بالمخزون ---
    # تم ربط backref باسم 'supplier_owner' للوصول للمورد من كائن المنتج
    products = db.relationship('Product', backref='supplier_owner', lazy=True, cascade="all, delete-orphan")

    @property
    def sovereign_id(self):
        """توليد الرقم السيادي للمحفظة والتعريف الموحد"""
        return f"MAH-9046{self.id}"

    @property
    def approval_label(self):
        """تسمية الحالة السيادية لاستخدامها في واجهة المستخدم"""
        return "معتمد ✅" if self.is_approved else "بانتظار المراجعة ⏳"

    def __repr__(self):
        return f'<Supplier: {self.name} | Sovereign ID: {self.sovereign_id}>'
