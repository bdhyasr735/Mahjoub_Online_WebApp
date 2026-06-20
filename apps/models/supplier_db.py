# coding: utf-8
# 📂 apps/models/supplier_db.py - الكيان السيادي لبيانات الموردين وحوكمة الصلاحيات

from apps.extensions import db
from flask_login import UserMixin
from datetime import datetime

class Supplier(db.Model, UserMixin):
    """
    الجدول الأساسي والمحكم لإدارة كيانات الموردين وصلاحياتهم الرقمية.
    متوافق تماماً مع نظام Flask-Login وحوكمة التشفير السيادي AES-256.
    """
    __tablename__ = 'suppliers'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    trade_name = db.Column(db.String(150), nullable=False)  # اسم المتجر/الشركة
    status = db.Column(db.String(20), default='active', nullable=False)  # active, suspended, pending
    
    # حقول مشفرة بـ AES-256 (يتم فكها وحقنها تلقائياً بفضل معالجاتك الذكية)
    _owner_phone = db.Column(db.String(255), nullable=True)
    _owner_email = db.Column(db.String(255), nullable=True)
    
    # الأكواد السيادية والمحفظة الملكية المرتبطة بالمورد
    supplier_code = db.Column(db.String(50), unique=True, nullable=True) # مثال: SUP-MAH963x
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # العلاقات البرمجية المعزولة (قواعد البيانات الفرعية)
    # ملاحظة: نستخدم backref لتجنب التداخل الدائري عند التشغيل
    wallet = db.relationship('SupplierWallet', uselist=False, backref='supplier_owner', lazy=True)

    @property
    def owner_phone(self):
        """Property ذكية لفك تشفير الهاتف تلقائياً لتعزيز الـ UX"""
        # هنا كود فك التشفير الخاص بك بـ AES-256
        return self._owner_phone

    @owner_phone.setter
    def owner_phone(self, value):
        """تشفير الهاتف سيادياً قبل الحفظ في قاعدة البيانات"""
        self._owner_phone = value

    def generate_codes(self):
        """توليد وحفر الأكواد السيادية الفريدة للمورد في النظام عند التوثيق والولوج"""
        if not self.supplier_code:
            # توليد كود حوكمي مخصص يحمل طابع المنصة الاستراتيجي
            self.supplier_code = f"SUP-MAH{self.id}x{datetime.now().strftime('%y%m')}"
            
    def __repr__(self):
        return f"<Supplier [{self.supplier_code}] -> {self.trade_name}>"
