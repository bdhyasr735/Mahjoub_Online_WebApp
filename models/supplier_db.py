# coding: utf-8
from models.admin_db import db  # استيراد الكائن الموحد لضمان وحدة قاعدة البيانات
from datetime import datetime

class Supplier(db.Model):
    """
    جدول بيانات الموردين في منظومة محجوب أونلاين
    هذا الجدول يمثل المستودع الرقمي لبيانات الموردين المعتمدين سيادياً
    """
    __tablename__ = 'suppliers'

    # الهوية الرقمية
    id = db.Column(db.Integer, primary_key=True)
    sovereign_id = db.Column(db.String(50), unique=True)  # المعرف السيادي الفريد (مثل: SUP-2026-XXXX)
    
    # بيانات الوصول والاعتماد
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100))
    
    # تفاصيل النشاط التجاري
    trade_name = db.Column(db.String(150))               # الاسم التجاري للمنشأة
    activity_type = db.Column(db.String(50))             # نوع النشاط (تجزئة، جملة، إلخ)
    owner_name = db.Column(db.String(150), nullable=False) # اسم المالك المعني
    identity_type = db.Column(db.String(50))             # نوع الهوية (شخصية، عائلية، تجارية)
    
    # بيانات التواصل
    phone = db.Column(db.String(20))
    
    # البيانات المالية (المحفظة السيادية)
    bank_name = db.Column(db.String(100))                # اسم البنك أو المحفظة الإلكترونية
    bank_acc = db.Column(db.String(100))                 # رقم الحساب أو الهاتف المرتبط بالدفع
    
    # النطاق الجغرافي (اليمن)
    province = db.Column(db.String(50))                  # المحافظة
    district = db.Column(db.String(50))                  # المديرية
    address_detail = db.Column(db.Text)                  # العنوان التفصيلي
    
    # التوثيق الزمني
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Supplier {self.trade_name if self.trade_name else self.username}>'
