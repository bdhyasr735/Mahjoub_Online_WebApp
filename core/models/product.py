from core import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    # ربط المنتج بالمورد (صاحب المنتج)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    
    # تفاصيل المنتج الأساسية
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False, default=0.0)
    stock = db.Column(db.Integer, default=0)
    
    # إدارة المحتوى (الصور والتصنيفات)
    image_url = db.Column(db.String(500)) # رابط الصورة من "قمرة" أو السيرفر
    category = db.Column(db.String(50))
    
    # التوقيت والحالة
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True) # متاح للبيع أو مخفي

    def __repr__(self):
        return f'<Product {self.name} - Price: {self.price}>'
