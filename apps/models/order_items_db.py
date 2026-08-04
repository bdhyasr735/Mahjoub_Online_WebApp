# coding: utf-8
# 📂 apps/models/order_items_db.py

from apps.extensions import db

class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(50), db.ForeignKey('orders.id'), nullable=False)
    supplier_id = db.Column(db.Integer, nullable=True)
    product_name = db.Column(db.String(255), nullable=True)
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float, default=0.0)

    def __repr__(self):
        return f'<OrderItem {self.id} for Order {self.order_id}>'
