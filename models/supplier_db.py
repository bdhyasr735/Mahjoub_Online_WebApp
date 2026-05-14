# coding: utf-8
from models.admin_db import db  # استيراد الكائن الموحد لضمان وحدة قاعدة البيانات
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Supplier(db.Model):
    """
    جدول بيانات الموردين في منظومة محجوب أونلاين
    يمثل المستودع الرقمي لبيانات الموردين المعتمدين سيادياً وفق رؤية 2026
    """
    __tablename__ = 'suppliers'

    # --- الهوية الرقمية السيادية ---
    id = db.Column(db.Integer, primary_key=True)
    # المعرف الموحد الثابت (مثل: SUP-WEL-MAH9631)
    sovereign_id = db.Column(db.String(50), unique=True, nullable=False) 
    
    # --- بيانات الوصول والاعتماد ---
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)  # كلمة المرور المشفرة
    email = db.Column(db.String(100), nullable=True)
    
    # --- تفاصيل النشاط التجاري والهوية ---
    trade_name = db.Column(db.String(150), nullable=False)    # الاسم التجاري للمنشأة
    activity_type = db.Column(db.String(50))                 # فئة المورد (جملة، تجزئة، إلخ)
    owner_name = db.Column(db.String(150), nullable=False)   # اسم المالك الكامل
    identity_type = db.Column(db.String(50))                 # نوع الوثيقة (بطاقة، سجل تجاري، إلخ)
    identity_number = db.Column(db.String(50), nullable=False) # رقم الوثيقة (العمود المضاف)
    identity_image = db.Column(db.String(255))               # مسار صورة الوثيقة المؤرشفة
    
    # --- بيانات التواصل ---
    owner_phone = db.Column(db.String(20), nullable=True)    # تلفون المالك الشخصي
    shop_phone = db.Column(db.String(20), nullable=False)    # هاتف المنشأة (أساسي في التحقق)
    
    # --- النظام المالي (الربط السيادي) ---
    fin_type = db.Column(db.String(50))                      # تصنيف الجهة (بنوك / صرافة)
    bank_name = db.Column(db.String(100), nullable=False)    # اسم البنك أو شركة الصرافة
    bank_acc = db.Column(db.String(100), nullable=False)     # رقم حساب التحويلات
    
    # --- النطاق الجغرافي (الجمهورية اليمنية) ---
    province = db.Column(db.String(50), nullable=False)      # المحافظة (الحديدة، عدن، تعز...)
    district = db.Column(db.String(50))                      # المديرية
    address_detail = db.Column(db.Text)                      # العنوان التفصيلي
    
    # --- التوثيق والرقابة ---
    is_active = db.Column(db.Boolean, default=True)          # حالة الاعتماد (نشط/موقف)
    created_at = db.Column(db.DateTime, default=datetime.utcnow) # تاريخ التعميد

    # --- وظائف إضافية للأمان والتعامل مع البيانات ---
    
    def set_password(self, password):
        """تشفير كلمة المرور قبل حفظها"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """التحقق من صحة كلمة المرور"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Supplier {self.trade_name} | ID: {self.sovereign_id}>'
