# coding: utf-8
# 📂 apps/models/product_supplier_map.py

import os
from datetime import datetime
from cryptography.fernet import Fernet
from apps.extensions import db

class ProductSupplierMapping(db.Model):
    """
    جدول الربط السيادي: يربط فقط بين منتج قمرة (qid) والمورد (supplier_id).
    المصدر الأساسي لكل التفاصيل (الاسم، السعر، المخزون) يظل "قمرة".
    """
    __tablename__ = 'product_supplier_mapping'

    # [فهرسة]: للبحث فائق السرعة
    __table_args__ = (
        db.Index('idx_map_qid', 'product_qid'),
        db.Index('idx_map_supplier', 'supplier_id'),
        {'extend_existing': True}
    )

    id = db.Column(db.Integer, primary_key=True)
    
    # المعرف الفريد لمنتج قمرة (لا غنى عنه)
    product_qid = db.Column(db.String(255), nullable=False, unique=True)
    
    # المعرف الخاص بالمورد في نظامنا (الرابط)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    
    # [تشفير سيادي]: ملاحظات إدارية خاصة بك فقط حول هذا الربط
    _internal_notes_enc = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقة مع المورد
    supplier = db.relationship('Supplier', backref='product_mappings', lazy='joined')

    # --- نظام التشفير ---
    @staticmethod
    def _get_key():
        key = os.environ.get('ENCRYPTION_KEY')
        return key.encode() if key else b'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8Vq='

    @property
    def internal_notes(self):
        if not self._internal_notes_enc: return None
        try:
            return Fernet(self._get_key()).decrypt(self._internal_notes_enc.encode()).decode()
        except Exception: return None

    @internal_notes.setter
    def internal_notes(self, value):
        if value:
            self._internal_notes_enc = Fernet(self._get_key()).encrypt(str(value).encode()).decode()
        else:
            self._internal_notes_enc = None

    def __repr__(self):
        return f"<Mapping qid={self.product_qid} supplier_id={self.supplier_id}>"
