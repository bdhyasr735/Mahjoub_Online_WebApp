from core import db
from datetime import datetime
from flask_login import UserMixin

# جدول الإدارة العليا (القائد علي ومساعدوه)
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='admin') # صلاحيات كاملة للتعديل
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# جدول شركاء النجاح (الموردين)
class Supplier(db.Model, UserMixin):
    __tablename__ = 'supplier'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=True) 
    phone = db.Column(db.String(20), nullable=True)
    
    # محفظة المورد - تظهر الرصيد المالي المرتبط بآيدي المورد
    wallet_balance = db.Column(db.Float, default=0.0) 
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    products = db.relationship('Product', backref='owner', lazy=True)

# جدول ترسانة المنتجات - مركز التحكم في البيانات
class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    
    # بيانات قابلة للتعديل من قبل الإدارة فقط
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(100), nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    
    # السياسة المالية
    original_price = db.Column(db.Float, nullable=False, default=0.0) # سعر التكلفة (يدخله المورد)
    sale_price = db.Column(db.Float, nullable=False, default=0.0)     # سعر البيع (تحدده الإدارة)
    
    # التحكم في العرض والربط
    is_synced = db.Column(db.Boolean, default=False) # هل تمت الموافقة والنشر في قمرة؟
    status = db.Column(db.String(50), default='pending') # تبدأ بـ pending حتى تعتمدها الإدارة
    
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Product {self.name} | Cost: {self.original_price} | Wallet ID: {self.supplier_id}>'
