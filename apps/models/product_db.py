# coding: utf-8
# 📂 apps/models/product_db.py

import os
from datetime import datetime
from cryptography.fernet import Fernet
from apps.extensions import db

class Product(db.Model):
    """جدول المنتجات المربوط بمنصة قمرة: بنية متكاملة للبيانات."""
    __tablename__ = 'products'
    
    __table_args__ = (
        db.Index('idx_prod_qid', 'qid', unique=True),
        db.Index('idx_prod_sku', 'sku'),
        {'extend_existing': True}
    )
    
    # المعرفات الأساسية
    id = db.Column(db.Integer, primary_key=True)
    qid = db.Column(db.String(100), nullable=False) # المعرف الفريد من قمرة
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=True)
    
    # البيانات الأساسية للمنتج
    title = db.Column(db.String(255), nullable=False)
    sku = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    
    # تفاصيل المبيعات والأسعار
    cost_price = db.Column(db.Float, default=0.0)
    quantity = db.Column(db.Integer, default=0)
    currency = db.Column(db.String(10), default='SAR')
    
    # تفاصيل الشحن والوزن (من الـ GraphQL)
    image_url = db.Column(db.String(500), nullable=True)
    weight_val = db.Column(db.Float, nullable=True)
    weight_unit = db.Column(db.String(20), nullable=True)
    dimensions = db.Column(db.String(100), nullable=True) # تخزين كـ نص أو JSON
    
    # الحالة والتدقيق
    status = db.Column(db.String(50), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_sync = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقة
    supplier = db.relationship('Supplier', backref='products', lazy='select')

    # --- نظام التشفير ---
    @staticmethod
    def _get_key():
        key = os.environ.get('ENCRYPTION_KEY')
        return key.encode() if key else b'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8Vq='

    # ملاحظة: تم تبسيط التعامل مع السعر ليكون Float مباشراً لسرعة العرض، 
    # يمكنك استخدام _cost_price_enc إذا كنت تفضل التشفير.
