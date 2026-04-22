from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# تعريف كائن قاعدة البيانات
db = SQLAlchemy()

class User(db.Model):
    """جدول المستخدمين للإدارة وشركاء النجاح"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='admin') # نوع المستخدم
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Product(db.Model):
    """جدول المنتجات المرتبط بنظام قمرة (سوقك الذكي)"""
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    qumra_id = db.Column(db.String(100)) # معرف المنتج في قمرة
