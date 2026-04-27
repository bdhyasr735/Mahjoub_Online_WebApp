from datetime import datetime
from flask_login import UserMixin
# استيراد db من النواة المركزية لضمان وحدة المحرك السيادي ومنع التكرار
from core import db

# --- 1. جدول المستخدمين الموحد (الأساس السيادي للهوية) ---
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='admin') # 'admin' للقائد أو 'supplier' للموردين
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # ربط الهوية ببروفايل المورد (علاقة 1 إلى 1)
    # تسمح لنا بالوصول للمحافظ المالية عبر: current_user.supplier_profile
    supplier_profile = db.relationship('Supplier', backref='user_account', uselist=False)

# --- 2. جدول الموردين (الترسانة المالية والبيانات التجارية) ---
class Supplier(db.Model):
    __tablename__ = 'supplier'
    id = db.Column(db.Integer, primary_key=True)
    # المفتاح الأجنبي لربط المورد بحساب مستخدم
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    trade_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    province = db.Column(db.String(50), nullable=True) # مثل: الحديدة، عدن
    
    # المحافظ المالية السيادية بالعملات الثلاث
    wallet_balance = db.Column(db.Numeric(10, 2), default=0.00) # الرصيد الإجمالي التقديري
    wallet_usd = db.Column(db.Numeric(10, 2), default=0.00)      # الدولار الأمريكي
    wallet_sar = db.Column(db.Numeric(10, 2), default=0.00)      # الريال السعودي
    wallet_yer = db.Column(db.Numeric(10, 2), default=0.00)      # الريال اليمني
    
    is_approved = db.Column(db.Boolean, default=False) # تعميد القائد علي محجوب
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # ربط المورد بمنتجاته (علاقة 1 إلى متعدد)
    products = db.relationship('Product', backref='owner_supplier', lazy=True, cascade="all, delete-orphan")

# --- 3. جدول المنتجات (الارتباط التقني مع قمرة) ---
class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    q_product_id = db.Column(db.String(100), unique=True, nullable=True) # ID المنتج في منصة قمرة
    q_collection_id = db.Column(db.String(100), nullable=True)           # تصنيف القسم
    
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    cost_price = db.Column(db.Numeric(10, 2), nullable=False, default=0.00) # سعر التكلفة من المورد
    sale_price = db.Column(db.Numeric(10, 2), nullable=True)                # سعر البيع للمستهلك
    
    status = db.Column(db.String(50), default='pending') # pending, active, rejected
    is_active = db.Column(db.Boolean, default=False)      # هل يظهر في المتجر؟
    is_synced = db.Column(db.Boolean, default=False)      # هل تمت المزامنة مع قمرة؟
    
    # المفتاح الأجنبي لربط المنتج بمورده الأصلي
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
