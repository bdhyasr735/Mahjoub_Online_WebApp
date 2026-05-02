from core import db

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    store_name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(200)) # عدن، الخوخة، المخا، حيس
    is_verified = db.Column(db.Boolean, default=False)
    
    # هذه العلاقة ستبحث الآن عن supplier_id في جدول المنتجات وستجده
    products = db.relationship('Product', backref='owner_supplier', lazy='dynamic', cascade="all, delete-orphan")
