from flask_sqlalchemy import SQLAlchemy

# تعريف قاعدة البيانات
db = SQLAlchemy()

# 1. جدول الموردين (ضروري لأن لوحة التحكم تعتمد عليه)
class Supplier(db.Model):
    __tablename__ = 'suppliers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    status = db.Column(db.String(20), default='active')

# 2. جدول المنتجات (مطابق لبيانات قمرة في الصور)
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    qumra_id = db.Column(db.String(100), unique=True) # الـ _id من قمرة
    name = db.Column(db.String(200))                  # الـ title من قمرة
    handle = db.Column(db.String(200))                # الـ handle من قمرة
    price = db.Column(db.Float, default=0.0)
    stock = db.Column(db.Integer, default=0)
    
    # ربط المنتج بالمورد (اختياري ولكن يفضل وجوده)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
