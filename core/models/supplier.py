# core/models/supplier.py
import os
import sys
from datetime import datetime

# --- بروتوكول تثبيت المسارات (Railway Patch) ---
# هذا الجزء يضمن إخبار السيرفر بمكان وجود المجلد الرئيسي للمشروع
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

# استيراد db باستخدام مسار مرن يتكيف مع السيرفر
try:
    from core.extensions import db
except (ImportError, ModuleNotFoundError):
    try:
        from extensions import db
    except (ImportError, ModuleNotFoundError):
        # الحل الأخير في حالة فشل كل المسارات التقليدية
        from ..extensions import db

class Supplier(db.Model):
    """
    نموذج الموردين لمنظومة محجوب أونلاين
    المستخدمة في مناطق (الخوخة، حيس، المخا، عدن)
    """
    __tablename__ = 'suppliers'
    
    # المعرفات
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    
    # البيانات الشخصية والتجارية
    owner_name = db.Column(db.String(150), nullable=False)
    trade_name = db.Column(db.String(150), nullable=False)
    activity_type = db.Column(db.String(100))
    
    # التوثيق
    id_type = db.Column(db.String(50))
    id_card_number = db.Column(db.String(50))
    
    # الجغرافيا والاتصال
    phone = db.Column(db.String(20), nullable=False)
    province = db.Column(db.String(100))
    district = db.Column(db.String(100))
    address_detail = db.Column(db.Text)
    
    # الربط المالي
    e_wallet = db.Column(db.String(100), unique=True)
    bank_name = db.Column(db.String(100))
    bank_acc = db.Column(db.String(100))
    
    # حالة الحساب
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Supplier {self.trade_name}>'
