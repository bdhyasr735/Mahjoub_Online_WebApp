# core/models/supplier.py
from datetime import datetime
from flask_login import UserMixin
from core.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class Supplier(db.Model, UserMixin):
    """ موديل المورد الأساسي - منصة محجوب أونلاين """
    __tablename__ = 'suppliers'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # 1. التأمين في الجدول: الحقول فريدة (Unique) ولا تقبل الفراغ
    sovereign_id = db.Column(db.String(50), unique=True, nullable=True)
    wallet_id = db.Column(db.String(50), unique=True, nullable=True)
    
    # اسم المستخدم يدوي (عربي/إنجليزي)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    trade_name = db.Column(db.String(150), nullable=False)
    owner_name = db.Column(db.String(150))
    activity_type = db.Column(db.String(100))
    identity_type = db.Column(db.String(50))
    identity_image = db.Column(db.String(255))
    
    phone = db.Column(db.String(20))
    email = db.Column(db.String(150))
    province = db.Column(db.String(100))
    district = db.Column(db.String(100))
    address_detail = db.Column(db.Text)
    
    # البيانات المالية
    bank_name = db.Column(db.String(150))
    bank_acc = db.Column(db.String(100))
    balance_yer = db.Column(db.Float, default=0.0)
    balance_sar = db.Column(db.Float, default=0.0)
    balance_usd = db.Column(db.Float, default=0.0)
    
    # حقول الحالة والرتبة (تم إضافة حقل tier هنا لحل مشكلة Railway)
    status = db.Column(db.String(20), default='active')
    tier = db.Column(db.String(50), default='مبتدئ') # رتبة المورد: سيادي، ذهبي، مبتدئ
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 2. المحرك الذكي: دالة لتوليد المعرفات تلقائياً قبل الحفظ
    def generate_sovereign_codes(self):
        """توليد المعرف السيادي ورقم المحفظة بناءً على الـ ID"""
        if not self.id:
            last_supplier = Supplier.query.order_by(Supplier.id.desc()).first()
            next_num = (last_supplier.id + 1) if last_supplier else 1
        else:
            next_num = self.id
            
        self.sovereign_id = f"SUP-MHA_963{next_num}"
        self.wallet_id = f"WEL-MAH-963{next_num}"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # 3. محرك التحويل الرقمي (JSON)
    def to_dict(self):
        """تحويل الكيان إلى قاموس لسهولة استخدامه في الـ API والواجهات"""
        return {
            "id": self.id,
            "sovereign_id": self.sovereign_id,
            "username": self.username,
            "trade_name": self.trade_name,
            "owner_name": self.owner_name,
            "phone": self.phone,
            "province": self.province,
            "district": self.district,
            "status": self.status,
            "tier": self.tier,
            "balance_yer": self.balance_yer,
            "balance_sar": self.balance_sar,
            "balance_usd": self.balance_usd,
            "created_at": self.created_at.strftime('%Y-%m-%d')
        }

    def __repr__(self):
        return f"<Supplier {self.trade_name} | {self.sovereign_id}>"

class SupplierStaff(db.Model):
    __tablename__ = 'supplier_staff'
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    name = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(100))
    status = db.Column(db.String(20), default='active')
    supplier = db.relationship('Supplier', backref=db.backref('staff_members', lazy=True))
