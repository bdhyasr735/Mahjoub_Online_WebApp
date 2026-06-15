# 📂 apps/models/product_db.py
from apps.extensions import db

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    qid = db.Column(db.String(100), unique=True, nullable=False) # المعرف الفريد من قمرة
    title = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, default=0.0)
    compare_at_price = db.Column(db.Float, default=0.0)
    quantity = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default='active')
    image_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.String(50), nullable=True)
