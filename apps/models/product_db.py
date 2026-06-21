# coding: utf-8
# 📂 apps/models/product_db.py - جسر المنتجات السيادي (مؤمن ومفهرس للربط السريع)

from apps.extensions import db
from datetime import datetime
from apps.utils.security import AESCipher

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # ⚡ فهرسة المورد للربط السريع
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # ⚡ معرف قمرة مفهرس للبحث عن المنتج فور وصول الـ Webhook
    qamrah_product_id = db.Column(db.String(100), unique=True, index=True, nullable=True)
    
    product_name = db.Column(db.String(255), nullable=False, index=True)
    
    # ⚡ SKU مفهرس كونه المفتاح الأهم للمطابقة بين الأنظمة
    sku = db.Column(db.String(100), unique=True, nullable=False, index=True)
    
    # 🔐 حقل مشفر: سعر التكلفة (سر تجاري)
    _cost_price_enc = db.Column('cost_price', db.String(255), nullable=False)
    
    # سعر البيع (ليس سراً، نحتاجه للفلترة والتقارير المالية)
    market_sale_price = db.Column(db.Numeric(16, 2), nullable=False, index=True)
    
    currency = db.Column(db.String(10), default='YER', nullable=False, index=True)
    stock_quantity = db.Column(db.Integer, default=0, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # 💎 بوابات الوصول الآمن لسعر التكلفة
    @property
    def cost_price(self):
        val = AESCipher.decrypt(self._cost_price_enc)
        return float(val) if val else 0.0

    @cost_price.setter
    def cost_price(self, value):
        self._cost_price_enc = AESCipher.encrypt(str(value))

    # روابط العلاقات
    supplier = db.relationship('Supplier', backref='products')

    def __repr__(self):
        return f'<Product {self.sku} - {self.product_name}>'
