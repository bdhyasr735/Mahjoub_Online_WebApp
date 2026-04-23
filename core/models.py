from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone_whatsapp = db.Column(db.String(20), unique=True, nullable=False)
    status = db.Column(db.String(20), default='pending') # pending, active
    
    # علاقة مع المنتجات
    products = db.relationship('Product', backref='supplier', lazy=True)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    qumra_id = db.Column(db.String(100), unique=True) # المعرف من قمرة (ظاهر في صورتك)
    name = db.Column(db.String(200))
    price = db.Column(db.Float)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
