# 📂 apps/models/product_db.py

import os
from datetime import datetime
from cryptography.fernet import Fernet
from apps.extensions import db

class Product(db.Model):
    """جدول المنتجات المربوط بمنصة قمرة: فهرسة للسرعة وربط حي."""
    __tablename__ = 'products'
    
    __table_args__ = (
        db.Index('idx_prod_supplier_qid', 'supplier_id', 'qid', unique=True),
        db.Index('idx_prod_sku', 'sku'),
        {'extend_existing': True}
    )
    
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    
    # المعرف القادم من قمرة (qid)
    qid = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    sku = db.Column(db.String(100), nullable=True)
    
    # [تشفير]: سعر التكلفة الخاص بالمورد
    _cost_price_enc = db.Column(db.String(255), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_sync = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقة: تم تغيير lazy='joined' إلى 'select' لمنع خطأ الربط (JOIN) في Postgres
    # عند الحاجة لجلب المورد، يمكنك القيام بذلك يدوياً أو عبر db.joinedload(Product.supplier) في استعلام معين
    supplier = db.relationship('Supplier', backref='products', lazy='select')

    # --- نظام التشفير (نفس مفتاح Supplier) ---
    @staticmethod
    def _get_key():
        key = os.environ.get('ENCRYPTION_KEY')
        return key.encode() if key else b'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8Vq='

    @property
    def cost_price(self):
        if not self._cost_price_enc: return None
        try:
            return float(Fernet(self._get_key()).decrypt(self._cost_price_enc.encode()).decode())
        except: return None

    @cost_price.setter
    def cost_price(self, value):
        if value:
            self._cost_price_enc = Fernet(self._get_key()).encrypt(str(value).encode()).decode()
