from core import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy.exc import InternalError, ProgrammingError

# --- 1. كلاس المستخدم (الهوية والرقابة السيادية) ---
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True} # لضمان تحديث الجداول في Railway بدون انهيار

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), default='vendor') # التمييز بين الإدارة (Admin) والموردين
    is_active_account = db.Column(db.Boolean, default=True)

    # الربط المباشر ببروفايل المورد (علاقة رأس برأس)
    # ملاحظة: حذفنا الاستيراد الخارجي ودمجنا العلاقة هنا مباشرة
    vendor_profile = db.relationship('Vendor', backref='user', uselist=False, cascade="all, delete-orphan")

    def set_password(self, password):
        """تشفير كلمة المرور لتعزيز الأمن الرقمي"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """التحقق السيادي من الهوية عند تسجيل الدخول"""
        if not self.password_hash: return False
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self):
        """التحقق من نشاط الحساب مع حماية القاعدة من التوقف المفاجئ"""
        try:
            return self.is_active_account
        except (InternalError, ProgrammingError, Exception):
            db.session.rollback()
            return True 

    def get_id(self):
        return str(self.id)

# --- 2. كلاس المورد (Vendor) - الهوية المالية والتقنية ---
class Vendor(db.Model):
    __tablename__ = 'vendors'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    # المعرفات السيادية لمحجوب أونلاين
    supplier_id = db.Column(db.String(50), unique=True) # المعرف مثل: MAH-963
    trade_name = db.Column(db.String(150)) # الاسم التجاري للمورد
    owner_name = db.Column(db.String(150)) # اسم المالك
    phone = db.Column(db.String(20))
    e_wallet = db.Column(db.String(100), unique=True) # المحفظة الذكية: W-MAH
    
    # الهندسة المالية (الأرصدة الثلاثة لضمان الاستقرار المالي)
    balance_yer = db.Column(db.Float, default=0.0) # الريال اليمني
    balance_sar = db.Column(db.Float, default=0.0) # الريال السعودي
    balance_usd = db.Column(db.Float, default=0.0) # الدولار الأمريكي
    
    # بيانات النشاط والموقع الجغرافي
    activity_type = db.Column(db.String(100))
    province = db.Column(db.String(100)) # المحافظة (عدن، الخوخة، موزع، إلخ)
    district = db.Column(db.String(100)) # المديرية
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Vendor {self.trade_name} - ID: {self.supplier_id}>"

# --- 3. إدارة طلبات السحب (الرقابة على التدفقات المالية) ---
class WithdrawRequest(db.Model):
    __tablename__ = 'withdraw_requests'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10)) # العملة المسحوبة (YER, SAR, USD)
    status = db.Column(db.String(20), default='pending') # حالة الطلب (قيد الانتظار، مقبول، مرفوض)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # علاقة للوصول السريع لبيانات المورد من داخل طلب السحب
    vendor_rel = db.relationship('Vendor', backref=db.backref('withdrawals', lazy=True))
