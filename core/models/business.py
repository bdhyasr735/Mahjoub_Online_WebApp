from core import db
from datetime import datetime

class Supplier(db.Model):
    __tablename__ = 'suppliers'

    id = db.Column(db.Integer, primary_key=True)
    # ربط المورد بالمستخدم (إذا كان مطلوباً)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=True)
    
    # المعرفات السيادية
    sovereign_id = db.Column(db.String(20), unique=True, nullable=False)
    e_wallet = db.Column(db.String(50), unique=True, nullable=False)
    
    # بيانات النشاط
    trade_name = db.Column(db.String(255), nullable=False)
    owner_name = db.Column(db.String(255), nullable=False)
    activity_type = db.Column(db.String(100), nullable=False)
    
    # بيانات الهوية والاتصال
    id_type = db.Column(db.String(50), nullable=False)
    id_card_number = db.Column(db.String(100), nullable=False)
    id_image = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(20), nullable=False)
    
    # الموقع الجغرافي
    province = db.Column(db.String(100), nullable=False)
    district = db.Column(db.String(100), nullable=False)
    address_detail = db.Column(db.Text, nullable=False)
    
    # الربط المالي
    fin_type = db.Column(db.String(20), default='banks')
    bank_name = db.Column(db.String(150), nullable=False)
    bank_acc = db.Column(db.String(100), nullable=False)
    
    # التوقيت والحالة
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Supplier {self.trade_name}>"

# ملاحظة: إذا كان هناك ملفات أخرى تحاول استيراد 'Province' ككلاس منفصل، 
# يجب تعديلها لتستخدم 'Supplier.province' أو إزالة الاستيراد الخاطئ.
