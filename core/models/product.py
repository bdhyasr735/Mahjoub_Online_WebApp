from core import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(100), nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    
    # السياسة المالية (التسعير)
    original_price = db.Column(db.Float, nullable=False, default=0.0) # سعر المورد
    sale_price = db.Column(db.Float, nullable=False, default=0.0)     # سعر البيع النهائي
    
    # الحالة والربط
    status = db.Column(db.String(50), default='pending') 
    is_synced = db.Column(db.Boolean, default=False) 
    
    # الربط بالمورد (شريك النجاح)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Product: {self.name} | SupplierID: {self.supplier_id}>'
