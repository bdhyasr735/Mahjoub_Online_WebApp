# coding: utf-8
# 📂 apps/models/order_items_db.py

from apps.extensions import db

class OrderItem(db.Model):
    """تفاصيل المنتجات داخل الطلب الواحد."""
    __tablename__ = 'order_items'

    # [فهرسة الأداء]: للربط السريع مع الطلبات
    __table_args__ = (
        db.Index('idx_item_order_id', 'order_id'),
        db.Index('idx_item_title', 'title'),
        {'extend_existing': True}
    )

    id = db.Column(db.Integer, primary_key=True)
    # الربط بالطلب الأساسي
    order_id = db.Column(db.String(100), db.ForeignKey('orders.id'), nullable=False)
    
    # تفاصيل المنتج القادمة من قمرة
    title = db.Column(db.String(255), nullable=False)
    qty = db.Column(db.Integer, default=1)
    subtotal = db.Column(db.Numeric(18, 2), default=0.00)
    
    # إضافات اختيارية لتطوير النظام مستقبلاً
    sku = db.Column(db.String(100), nullable=True) # رمز المنتج
    price_per_unit = db.Column(db.Numeric(18, 2), default=0.00) # سعر القطعة الواحدة
    
    # علاقة عكسية للوصول للمنتجات من داخل الطلب
    order = db.relationship('Order', backref=db.backref('items', cascade="all, delete-orphan"))

    def __repr__(self):
        return f'<OrderItem {self.title} | Qty: {self.qty}>'
