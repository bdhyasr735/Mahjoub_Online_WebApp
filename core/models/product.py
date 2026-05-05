from core import db
from datetime import datetime

# --- كلاس المنتجات (ترسانة السلع في محجوب أونلاين) ---
class Product(db.Model):
    __tablename__ = 'products'
    __table_args__ = {'extend_existing': True} # لضمان سلاسة التحديث في Railway

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False) # اسم المنتج (مثل: معوز تهامي، لابتوب Dell)
    
    # تفاصيل التسعير السيادي
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='YER') # العملة (YER, SAR, USD)
    
    # ربط المنتج بصاحبه (المؤسس علي محجوب أو مورد معتمد)
    # تم التعديل ليرتبط بجدول users لضمان عدم توقف النظام
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # بيانات المخزون والوصف
    stock_quantity = db.Column(db.Integer, default=0)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(100), nullable=True) # فئة المنتج
    
    # التوقيت الرقمي
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # علاقة للوصول السريع لبيانات صاحب المنتج
    owner = db.relationship('User', backref=db.backref('products', lazy=True))

    def __repr__(self):
        return f"<Product {self.name} - Price: {self.price}>"
