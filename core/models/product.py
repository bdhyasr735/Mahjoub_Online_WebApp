from core.extensions import db
from datetime import datetime
from sqlalchemy import event
from core.currency_engine import currency_engine # استدعاء المحرك المالي

class Product(db.Model):
    """
    نموذج المنتجات المطوّر - ترسانة السلع v3.7
    يدعم التسعير الديناميكي والربط السيادي بالموردين
    """
    __tablename__ = 'products'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    product_sid = db.Column(db.String(50), unique=True) # المعرف السيادي للمنتج
    name = db.Column(db.String(200), nullable=False)
    
    # --- هيكلة الأسعار السيادية ---
    # السعر الأساسي (سعر المورد)
    base_price = db.Column(db.Numeric(20, 2), nullable=False) 
    # العملة الأصلية للمنتج (SAR, USD, YER)
    currency = db.Column(db.String(10), default='YER') 
    
    # السعر النهائي للمستهلك (يتم حسابه تلقائياً عبر المحرك)
    final_price_yer = db.Column(db.Numeric(20, 2)) 
    
    # --- العلاقات السيادية ---
    # ربط المنتج بالمورد (المصدر الحقيقي للسلعة)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=True)
    # ربط المنتج بالمسؤول (الذي وافق على المنتج أو يملكه)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # --- المخزون والبيانات ---
    stock_quantity = db.Column(db.Integer, default=0)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(100), nullable=True)
    image_url = db.Column(db.String(255), nullable=True) # رابط صورة المنتج
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقات
    owner = db.relationship('User', backref=db.backref('managed_products', lazy=True))
    supplier = db.relationship('Supplier', backref=db.backref('products', lazy=True))

    def update_final_price(self):
        """تحديث السعر النهائي بالريال اليمني بناءً على محرك العملات وعمولة محجوب"""
        # تحويل السعر الأساسي للريال اليمني أولاً
        price_in_yer = currency_engine.convert_to_yer(self.base_price, self.currency)
        # حساب السعر النهائي مع إضافة عمولة المنصة (10% افتراضياً)
        self.final_price_yer = currency_engine.calculate_final_price(price_in_yer)
        return self.final_price_yer

    def to_dict(self):
        return {
            "id": self.id,
            "product_sid": self.product_sid or f"PROD_{self.id}",
            "name": self.name,
            "base_price": float(self.base_price),
            "final_price_yer": float(self.final_price_yer) if self.final_price_yer else 0,
            "currency": self.currency,
            "stock": self.stock_quantity,
            "supplier": self.supplier.trade_name if self.supplier else "المنصة",
            "category": self.category
        }

    def __repr__(self):
        return f"<Product {self.name} | Final Price: {self.final_price_yer} YER>"

# --- محرك التعميد التلقائي للمنتجات ---
@event.listens_for(Product, 'before_insert')
def before_product_insert(mapper, connection, target):
    """توليد المعرف وحساب السعر قبل الحفظ في القاعدة"""
    # سيتم توليد المعرف في الـ after_insert أو يدوياً هنا
    target.update_final_price()

@event.listens_for(Product, 'after_insert')
def after_product_insert(mapper, connection, target):
    table = Product.__table__
    connection.execute(
        table.update().
        where(table.c.id == target.id).
        values(product_sid=f"PROD_MAH_963{target.id}")
    )
