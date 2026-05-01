from core import db
from datetime import datetime

class Product(db.Model):
    """
    موديل المنتجات - قلب التجارة في منصة محجوب أونلاين.
    يدعم التصنيفات المتنوعة والعملة المعتمدة (SAR).
    """
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False) # اسم المنتج
    description = db.Column(db.Text, nullable=True)   # وصف المنتج
    
    # السعر والعملة (تم اعتماد SAR بناءً على التحديثات الأخيرة)
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='SAR') 
    
    # التصنيفات (ملابس، أدوات منزلية، إلكترونيات، إلخ)
    category = db.Column(db.String(100), nullable=False)
    
    # المخزون وحالة التوفر
    stock_quantity = db.Column(db.Integer, default=0)
    is_available = db.Column(db.Boolean, default=True)
    
    # الصور (تخزين مسار الصورة)
    image_url = db.Column(db.String(500), nullable=True)
    
    # الروابط مع الموردين
    supplier_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # التوقيت
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Product {self.name} - {self.price} {self.currency}>'

    def to_dict(self):
        """تحويل بيانات المنتج إلى قاموس لسهولة التعامل معها في الواجهات"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'currency': self.currency,
            'category': self.category,
            'stock': self.stock_quantity,
            'is_available': self.is_available,
            'image_url': self.image_url,
            'supplier_id': self.supplier_id,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
