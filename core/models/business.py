from core.extensions import db
from datetime import datetime
from sqlalchemy import event

class Order(db.Model):
    """
    نموذج الطلبات - نظام الحوكمة v3.8
    يدعم تتبع حالة الشحن، المعرفات السيادية، والربط المالي
    """
    __tablename__ = 'orders'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    order_sid = db.Column(db.String(50), unique=True) # المعرف السيادي للطلب (ORD_MAH_...)
    
    # ربط العميل
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # التفاصيل المالية (استخدام Numeric للدقة)
    total_amount = db.Column(db.Numeric(20, 2), nullable=False)
    currency = db.Column(db.String(10), default='YER')
    
    # نظام الحالات اللوني (يتوافق مع واجهة الإدارة)
    # [pending, processing, shipped, delivered, cancelled, refunded]
    status = db.Column(db.String(50), default='pending')
    
    # بيانات اللوجستيات
    shipping_address = db.Column(db.Text, nullable=True)
    contact_phone = db.Column(db.String(20), nullable=True)
    notes = db.Column(db.Text, nullable=True) # ملاحظات العميل أو الإدارة
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقات
    customer = db.relationship('User', backref=db.backref('orders', lazy=True))
    items = db.relationship('OrderItem', backref='order', cascade="all, delete-orphan", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "order_sid": self.order_sid or f"ORD_{self.id}",
            "customer": self.customer.username if self.customer else "N/A",
            "total": float(self.total_amount),
            "currency": self.currency,
            "status": self.status,
            "date": self.created_at.strftime('%Y-%m-%d %H:%M'),
            "items_count": len(self.items)
        }

class OrderItem(db.Model):
    """جدول تفاصيل الطلب - يربط المنتجات بالموردين في كل فاتورة"""
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=True) # لسهولة تصفية مستحقات الموردين
    
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Numeric(20, 2), nullable=False) # السعر وقت الشراء (لحفظ السجل المالي من التغير)

    # العلاقات
    product = db.relationship('Product')

# --- محرك التعميد التلقائي للطلبات ---
@event.listens_for(Order, 'after_insert')
def after_order_insert(mapper, connection, target):
    table = Order.__table__
    connection.execute(
        table.update().
        where(table.c.id == target.id).
        values(order_sid=f"ORD_MAH_963{target.id}")
    )
