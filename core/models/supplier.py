# core/models/supplier.py
from datetime import datetime
from flask_login import UserMixin
from core import db

class Supplier(db.Model, UserMixin):
    """ 
    موديل المورد السيادي: المرجع الأساسي لهيكلة البيانات.
    يرث من UserMixin لدعم محركات استعادة الهوية (Auth Loaders) تلقائياً.
    """
    __tablename__ = 'suppliers'
    
    # المعرفات السيادية
    id = db.Column(db.Integer, primary_key=True)
    sovereign_id = db.Column(db.String(50), unique=True)
    
    # البيانات الأساسية والتوثيق (متوافقة مع واجهة التعميد الملكية)
    trade_name = db.Column(db.String(150), nullable=False)
    owner_name = db.Column(db.String(150))
    activity_type = db.Column(db.String(100))
    identity_type = db.Column(db.String(50))
    
    # النطاق الجغرافي والاتصال
    province = db.Column(db.String(100))
    district = db.Column(db.String(100))
    address_detail = db.Column(db.Text)
    phone = db.Column(db.String(20))
    
    # الربط المالي (المحفظة الثلاثية)
    bank_name = db.Column(db.String(150))
    bank_acc = db.Column(db.String(100))
    balance_yer = db.Column(db.Float, default=0.0)
    balance_sar = db.Column(db.Float, default=0.0)
    balance_usd = db.Column(db.Float, default=0.0)
    
    # الحالة والتوثيق الزمني
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SupplierStaff(db.Model):
    """ طاقم العمل التابع للمورد - نافذة مستقلة لإدارة الموظفين """
    __tablename__ = 'supplier_staff'
    
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    name = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(100)) # مدير، مندوب، محاسب
    status = db.Column(db.String(20), default='active')
    
    # ربط العلاقة السيادية
    supplier = db.relationship('Supplier', backref=db.backref('staff_members', lazy=True))
