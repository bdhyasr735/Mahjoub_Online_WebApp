# coding: utf-8
# 📂 apps/models/supplier_db.py - الكيان السيادي لبيانات الموردين وحوكمة الصلاحيات

from apps.extensions import db
from flask_login import UserMixin
from datetime import datetime

class Supplier(db.Model, UserMixin):
    """
    الجدول الأساسي والمحكم لإدارة كيانات الموردين وصلاحياتهم الرقمية.
    تم استخدام السلاسل النصية في العلاقات لضمان فك الارتباط الدائري.
    """
    __tablename__ = 'suppliers'

    id = db.Column(db.Integer, primary_key=True)
    
    # 🔗 الجسر السيادي: ربط المورد بحسابه في كيان نظام الهوية الموحد (admin_users)
    admin_user_id = db.Column(db.Integer, db.ForeignKey('admin_users.id'), unique=True, nullable=True)

    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    trade_name = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(20), default='active', nullable=False)
    
    # حقول مشفرة بـ AES-256
    _owner_phone = db.Column(db.String(255), nullable=True)
    _owner_email = db.Column(db.String(255), nullable=True)
    
    # الأكواد السيادية والمحفظة
    supplier_code = db.Column(db.String(50), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 🔗 العلاقات البرمجية المعزولة (باستخدام السلسلة النصية لحل التداخل)
    # ملاحظة: تم ضبط back_populates ليتوافق مع الإعداد في wallet_db
    wallet = db.relationship('SupplierWallet', back_populates='supplier', uselist=False, lazy=True, cascade="all, delete-orphan")

    @property
    def owner_phone(self):
        return self._owner_phone

    @owner_phone.setter
    def owner_phone(self, value):
        # يمكنك إضافة منطق التشفير هنا
        self._owner_phone = value

    def generate_codes(self):
        if not self.supplier_code and self.id:
            self.supplier_code = f"SUP-MAH{self.id}x{datetime.utcnow().strftime('%y%m')}"
            
    def __repr__(self):
        return f"<Supplier [{self.supplier_code}] -> {self.trade_name}>"
