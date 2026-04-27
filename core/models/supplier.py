from core import db
from datetime import datetime

class Supplier(db.Model):
    """
    موديل المورد السيادي - نظام محجوب أونلاين MAH-9046
    يجمع بين الهوية الرقمية، الحوكمة المالية، والربط بالمخزون التيهامي.
    """
    __tablename__ = 'supplier'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # --- الربط بهوية المستخدم المركزية ---
    # نربطه بجدول User لتوحيد عملية الدخول (Login)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # --- 🛡️ نظام الرقابة والاعتماد السيادي ---
    is_approved = db.Column(db.Boolean, default=False) 
    status = db.Column(db.String(20), default='pending') # pending, active, suspended
    
    # --- تفاصيل المنشأة الجغرافية ---
    trade_name = db.Column(db.String(200)) # الاسم التجاري للمحل/الشركة
    full_name = db.Column(db.String(200))
    province = db.Column(db.String(100))   # المحافظة
    district = db.Column(db.String(100))   # المديرية
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True, nullable=False)

    # --- 💰 النظام المالي المتعدد والعمولات (Multicurrency Wallet) ---
    # الرصيد المعلق: أرباح من مبيعات قمرة لم تشحن بعد أو لم تؤكد
    balance_pending = db.Column(db.Float, default=0.0) 
    # الرصيد المتاح: أرباح جاهزة للسحب أو التحويل
    balance_available = db.Column(db.Float, default=0.0) 

    # الحسابات بالعملات المختلفة (كما كانت في كودك الأصلي)
    wallet_usd = db.Column(db.Float, default=0.0)      
    wallet_sar = db.Column(db.Float, default=0.0)      
    wallet_yer = db.Column(db.Float, default=0.0)      
    
    bank_name = db.Column(db.String(100))
    bank_acc = db.Column(db.String(100))
    fin_type = db.Column(db.String(50)) # نوع التصفية المالية
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # --- 📦 علاقة الربط بالمخزون ---
    # الربط بجدول المنتجات (Product)
    products = db.relationship('Product', backref='supplier_owner', lazy=True, cascade="all, delete-orphan")

    @property
    def sovereign_id(self):
        """توليد الرقم السيادي للمحفظة والتعريف الموحد MAH-9046X"""
        return f"MAH-9046{self.id}"

    @property
    def approval_label(self):
        """تسمية الحالة السيادية لاستخدامها في واجهة المستخدم"""
        return "معتمد ✅" if self.is_approved else "بانتظار المراجعة ⏳"

    def __repr__(self):
        return f'<Supplier: {self.trade_name} | Sovereign ID: {self.sovereign_id}>'
