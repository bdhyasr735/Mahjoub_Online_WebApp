# coding: utf-8
# 📂 apps/models/product_supplier_map.py

import os
from datetime import datetime
from cryptography.fernet import Fernet
from apps.extensions import db


class ProductSupplierMapping(db.Model):
    """
    جدول الربط السيادي: يربط بين منتج قمرة (qid) والمورد (supplier_id).
    يدعم تعديل وتحويل مسار المنتجات بسلاسة ودقة عالية.
    """
    __tablename__ = 'product_supplier_mapping'

    # [فهرسة]: للبحث فائق السرعة وإدارة المسارات
    __table_args__ = (
        db.Index('idx_map_qid', 'product_qid'),
        db.Index('idx_map_supplier', 'supplier_id'),
        # قيد مركب يمنع تكرار نفس المورد لنفس المنتج، مع السماح بتحويل المسار وتغيير الموردين بحرية
        db.UniqueConstraint('product_qid', 'supplier_id', name='uq_product_supplier_map'),
        {'extend_existing': True}
    )

    id = db.Column(db.Integer, primary_key=True)
    
    # المعرف الفريد لمنتج قمرة (بدون unique منفرد لتمكين تحويل المسار وتحديث المورد بسهولة)
    product_qid = db.Column(db.String(255), nullable=False)
    
    # المعرف الخاص بالمورد في نظامنا (الرابط)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    
    # ⚡️ استخدام Numeric(18, 2) لضمان دقة الحسابات المالية وتفادي مشاكل الأرقام العشرية (Float)
    price = db.Column(db.Numeric(18, 2), nullable=True)
    quantity = db.Column(db.Integer, nullable=True)
    
    # حالة الربط (نشط، معلق، محول، إلخ)
    status = db.Column(db.String(20), default='active', nullable=False)
    
    # [تشفير سيادي]: ملاحظات إدارية خاصة بك فقط حول هذا الربط
    _internal_notes_enc = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ✅ العلاقة مع المورد
    supplier = db.relationship('Supplier', back_populates='product_mappings', lazy='joined')

    # --- نظام التشفير ---
    @staticmethod
    def _get_key():
        key = os.environ.get('ENCRYPTION_KEY')
        return key.encode() if key else b'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8Vq='

    @property
    def internal_notes(self):
        if not self._internal_notes_enc:
            return None
        try:
            return Fernet(self._get_key()).decrypt(self._internal_notes_enc.encode()).decode()
        except Exception:
            return None

    @internal_notes.setter
    def internal_notes(self, value):
        if value:
            self._internal_notes_enc = Fernet(self._get_key()).encrypt(str(value).encode()).decode()
        else:
            self._internal_notes_enc = None

    def to_dict(self):
        """تحويل الربط إلى قاموس مع معالجة آمنة للقيم المالية والتاريخية"""
        return {
            'id': self.id,
            'product_qid': self.product_qid,
            'supplier_id': self.supplier_id,
            'price': float(self.price) if self.price is not None else 0.0,
            'quantity': self.quantity,
            'status': self.status,
            'internal_notes': self.internal_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f"<Mapping qid={self.product_qid} supplier_id={self.supplier_id} status={self.status}>"
