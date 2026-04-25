from core import db
from datetime import datetime
from flask_login import UserMixin

# 1. جدول الإدارة العليا (نظام التحكم المركزي)
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='admin')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 2. جدول شركاء النجاح (الموردين) - نظام التعميد السيادي
class Supplier(db.Model, UserMixin):
    __tablename__ = 'supplier'
    id = db.Column(db.Integer, primary_key=True)
    
    # بيانات الحساب (المستخدمة في تسجيل الدخول)
    name = db.Column(db.String(100), unique=True, nullable=False) # اسم المستخدم للدخول
    password = db.Column(db.String(200), nullable=False) # جعلناها nullable=False لضمان الحماية
    activity_type = db.Column(db.String(100))
    
    # بيانات المنشأة والموقع (التوثيق الميداني)
    trade_name = db.Column(db.String(200))
    full_name = db.Column(db.String(200))
    id_type = db.Column(db.String(50))
    province = db.Column(db.String(100))
    district = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True, nullable=False)

    # الربط المالي السيادي
    fin_type = db.Column(db.String(50))
    bank_name = db.Column(db.String(100))
    bank_acc = db.Column(db.String(100))
    wallet_balance = db.Column(db.Float, default=0.0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # ربط ترسانة المنتجات
    products = db.relationship('Product', backref='supplier_owner', lazy=True, cascade="all, delete-orphan")

    @property
    def sovereign_id(self):
        """
        توليد الرقم السيادي للمحفظة: MAH-9046 + ID المورد
        """
        base_sovereign = 9046
        return f"MAH-{base_sovereign}{self.id}"

# 3. جدول ترسانة المنتجات - مركز التحكم في البيانات
class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(100), nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    
    # السياسة المالية (التسعير اللامركزي)
    original_price = db.Column(db.Float, nullable=False, default=0.0) # سعر المورد
    sale_price = db.Column(db.Float, nullable=False, default=0.0)     # سعر المنصة
    
    # نظام الحالة والمزامنة
    status = db.Column(db.String(50), default='pending') 
    is_synced = db.Column(db.Boolean, default=False) 
    
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        # تمثيل المنتج بالرقم المالي للمورد لسهولة التتبع
        return f'<Product {self.name} | Wallet: MAH-9046{self.supplier_id}>'
