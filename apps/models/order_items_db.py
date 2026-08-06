# coding: utf-8
# 📂 apps/models/order_items_db.py

from apps.extensions import db

class OrderItem(db.Model):
    __tablename__ = 'order_items'

    __table_args__ = (
        db.Index('idx_item_order_id', 'order_id'),
        db.Index('idx_item_supplier_id', 'supplier_id'),
        {'extend_existing': True}
    )

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(100), db.ForeignKey('orders.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=True)
    
    product_qid = db.Column(db.String(255), nullable=True)
    product_name = db.Column(db.String(255), nullable=True)
    quantity = db.Column(db.Integer, default=1)
    
    # ⚡️ استخدام Numeric(18, 2) لدقة الحسابات وتجنب مشاكل الأرقام العشرية
    price = db.Column(db.Numeric(18, 2), default=0.00)
    
    # ✅ إضافة هذا السطر خصيصاً لمنع انهيار عملية الحفظ عند إرسال المزامنة للصورة
    product_image = db.Column(db.String(500), nullable=True)

    # العلاقة العكسية مع جدول الطلبات لحل خطأ الربط بشكل جذري
    order = db.relationship('Order', back_populates='items')
    
    # علاقة مباشرة مع المورد لتسهيل الاستعلامات
    supplier = db.relationship('Supplier', lazy='joined')

    def to_dict(self):
        """دالة ضرورية جداً لتحويل العنصر إلى JSON عند عرض الطلبات"""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'supplier_id': self.supplier_id,
            'product_qid': self.product_qid,
            'product_name': self.product_name,
            'quantity': self.quantity,
            'price': float(self.price) if self.price is not None else 0.0,
            'product_image': self.product_image
        }

    def __repr__(self):
        return f'<OrderItem {self.id} for Order {self.order_id}>'
