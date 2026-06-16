# coding: utf-8
# 📂 apps/models/product_db.py

from apps.extensions import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'products'
    
    # تأكد أن المعرف نصي (String) ليتناسب مع البيانات القادمة من قمرة
    id = db.Column(db.String(100), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, default=0.0)
    tag = db.Column(db.String(100), index=True) 
    image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # إضافة هذه الدالة تضمن استقرار الموديل أثناء المعالجة
    def __init__(self, **kwargs):
        super(Product, self).__init__(**kwargs)

    def __repr__(self):
        return f'<Product {self.title}>'
