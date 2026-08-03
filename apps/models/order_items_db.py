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
    
    productId = db.Column(db.String(100), nullable=True)
    title = db.Column(db.String(255), nullable=False)
    qty = db.Column(db.Integer, default=1)
    subtotal = db.Column(db.Numeric(18, 2), default=0.00)
    sku = db.Column(db.Text, nullable=True) 
    price_per_unit = db.Column(db.Numeric(18, 2), default=0.00) # سعر القطعة الواحدة
    _image_url = db.Column(db.Text, nullable=True)
    
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
            'image': {'fileUrl': self._image_url} if self._image_url else None
        }

    @property
    def quantity(self):
        """خاصية للتوافق مع تسمية quantity."""
        return self.qty

    @property
    def price(self):
        """خاصية للتوافق مع تسمية price."""
        return float(self.price_per_unit or 0.0)

    @property
    def totalPrice(self):
        return float(self.subtotal or (float(self.price_per_unit or 0.0) * self.qty))

    @property
    def image(self):
        """خاصية للتوافق مع استدعاء item.image مباشرة."""
        return self._image_url or ''

    def to_dict(self):
        """دالة تحويل عنصر الطلب إلى قاموس متوافق مع واجهات النظام."""
        return {
            'id': self.id,
            '_id': str(self.id),
            'order_id': self.order_id,
            'productId': self.productId,
            'title': self.title,
            'qty': self.qty,
            'quantity': self.qty,
            'price': float(self.price_per_unit or 0.0),
            'price_per_unit': float(self.price_per_unit or 0.0),
            'subtotal': float(self.subtotal or 0.0),
            'totalPrice': float(self.subtotal or 0.0),
            'sku': self.sku,
            'productData': {
                'title': self.title,
                'slug': self.sku,
                'image': {'fileUrl': self._image_url} if self._image_url else None
            }
        }

    def __repr__(self):
        return f'<OrderItem {self.title} | Qty: {self.qty}>'
