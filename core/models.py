from core import db
from datetime import datetime
from flask_login import UserMixin

# 1. جدول الإدارة العليا (القائد علي ومساعدوه)
# يمتلك الصلاحية الكاملة لتعديل أسعار البيع والموافقة على المنتجات
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='admin') # 'admin' للتحكم المطلق
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 2. جدول شركاء النجاح (الموردين)
# النظام اللامركزي يعتمد على ID المورد لربط محفظته بمنتجاته
class Supplier(db.Model, UserMixin):
    __tablename__ = 'supplier'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False) # اسم المورد العربي
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=True) 
    phone = db.Column(db.String(20), nullable=True)
    
    # محفظة المورد - تعكس الأرباح المستحقة من مبيعات منتجاته
    wallet_balance = db.Column(db.Float, default=0.0) 
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # ربط خلفي (Backref) يسهل جلب المنتجات عبر: supplier.products
    products = db.relationship('Product', backref='supplier_owner', lazy=True)

# 3. جدول ترسانة المنتجات - مركز التحكم في البيانات
class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    
    # بيانات التعريف الأساسية
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(100), nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    
    # السياسة المالية والربحية
    original_price = db.Column(db.Float, nullable=False, default=0.0) # يدخله المورد (التكلفة)
    sale_price = db.Column(db.Float, nullable=False, default=0.0)     # تحدده الإدارة (سعر البيع للجمهور)
    
    # نظام التحكم في الحالة (Workflow)
    # pending: قيد المراجعة، approved: معتمد، rejected: مرفوض
    status = db.Column(db.String(50), default='pending') 
    
    # نظام المزامنة مع المنصات الخارجية (قمرة وغيرها)
    is_synced = db.Column(db.Boolean, default=False) 
    
    # الربط السيادي بالمورد
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Product {self.name} | Cost: {self.original_price} | Supplier: {self.supplier_id}>'
