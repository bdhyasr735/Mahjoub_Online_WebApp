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
    
    # تفاصيل المنتج القادمة من المنصة
    title = db.Column(db.String(255), nullable=False)
    qty = db.Column(db.Integer, default=1)
    subtotal = db.Column(db.Numeric(18, 2), default=0.00)
    
    # [تعديل نوع الحقل]: تم استبدال String(100) بـ db.Text لاستيعاب الـ Slugs والنصوص الطويلة دون truncation error
    sku = db.Column(db.Text, nullable=True) 
    price_per_unit = db.Column(db.Numeric(18, 2), default=0.00) # سعر القطعة الواحدة
    
    # ربط العلاقة مع جدول الطلبات
    order = db.relationship(
        'Order', 
        back_populates='items'
    )

    # ==========================================
    # 🚀 خصائص التوافقية (Compatibility Properties)
    # لحل مشكلة UndefinedError في قوالب Jinja2
    # ==========================================

    @property
    def productData(self):
        """خاصية توافقية ترجع كائن مفردات يلائم استدلال `item.productData` في القالب."""
        return {
            'title': self.title or '',
            'slug': self.sku or '',
            'image': getattr(self, 'image_url', None) or ''
        }

    @property
    def quantity(self):
        """خاصية للتوافق مع تسمية quantity."""
        return self.qty

    @property
    def price(self):
        """خاصية للتوافق مع تسمية price."""
        return self.price_per_unit

    @property
    def image(self):
        """خاصية للتوافق مع استدعاء item.image مباشرة."""
        return getattr(self, 'image_url', '') or ''

    def __repr__(self):
        return f'<OrderItem {self.title} | Qty: {self.qty}>'
