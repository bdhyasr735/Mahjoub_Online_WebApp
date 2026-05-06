# core/models/supplier.py
import os
import sys
from datetime import datetime

# --- بروتوكول تثبيت المسارات (Railway Patch) ---
# يضمن هذا الجزء تعريف المسار الرئيسي للمشروع لضمان استقرار النظام على السيرفر
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

# استيراد db بمرونة لضمان العمل في بيئة Railway وجميع مناطق النطاق الجغرافي
try:
    from core.extensions import db
except (ImportError, ModuleNotFoundError):
    try:
        from extensions import db
    except (ImportError, ModuleNotFoundError):
        from ..extensions import db

class Supplier(db.Model):
    """
    نموذج الموردين المعتمد لمنظومة محجوب أونلاين
    يغطي العمليات في: (الخوخة، حيس، المخا، عدن)
    """
    __tablename__ = 'suppliers'
    
    # --- المعرفات الأساسية ---
    id = db.Column(db.Integer, primary_key=True) # المعرف المرتبط برقم 963
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    
    # --- البيانات الشخصية والتجارية ---
    owner_name = db.Column(db.String(150), nullable=False) # اسم مالك النشاط
    trade_name = db.Column(db.String(150), nullable=False) # الاسم التجاري
    activity_type = db.Column(db.String(100), nullable=False) # نوع النشاط التجاري
    
    # --- الرتبة الإدارية (مضافة للتوافق مع النافذة الأفقية) ---
    # هذا الحقل هو المسؤول عن "سحب" قيمة الرتبة في التصميم
    tier = db.Column(db.String(50), default='مبتدئ') 
    
    # --- بيانات التوثيق الرسمية ---
    id_type = db.Column(db.String(50), nullable=False) # (شخصية/جواز/عائلية)
    id_card_number = db.Column(db.String(50), nullable=False) 
    
    # --- الجغرافيا وقنوات الاتصال ---
    phone = db.Column(db.String(20), nullable=False) # رقم التواصل الأساسي
    province = db.Column(db.String(100), nullable=False) # المحافظة
    district = db.Column(db.String(100), nullable=False) # المديرية
    address_detail = db.Column(db.Text, nullable=False) # العنوان التفصيلي
    
    # --- الربط المالي (التعميد المالي السيادي) ---
    e_wallet = db.Column(db.String(100), unique=True, nullable=False) # رقم المحفظة
    bank_name = db.Column(db.String(100), nullable=False) # اسم البنك
    bank_acc = db.Column(db.String(100), nullable=False) # رقم الحساب
    
    # --- حالة الحساب السحابي ---
    status = db.Column(db.String(20), default='active') # (نشط/معلق)
    created_at = db.Column(db.DateTime, default=datetime.utcnow) # تاريخ التعميد

    def __repr__(self):
        return f'<Supplier {self.trade_name} - {self.e_wallet} - {self.tier}>'
