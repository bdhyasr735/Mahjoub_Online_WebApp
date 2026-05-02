from core import db  # استيراد كائن db المعرف في __init__.py الخاص بـ core
from datetime import datetime

class Vendor(db.Model):
    __tablename__ = 'vendors'

    # --- الحقول الأساسية ---
    id = db.Column(db.Integer, primary_key=True)
    
    # الربط مع المستخدم (User Model)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # --- بيانات الهوية والملك والوثائق ---
    owner_name = db.Column(db.String(255), nullable=False)
    id_type = db.Column(db.String(100), nullable=False)
    id_card_number = db.Column(db.String(50), nullable=False)
    
    # الحقل المحدث: تخزين مسار صورة الهوية أو السجل التجاري (أرشفة ضوئية)
    id_image_path = db.Column(db.String(500), nullable=True) 
    
    # --- بيانات المنشأة والنشاط ---
    trade_name = db.Column(db.String(255), nullable=False)
    activity_type = db.Column(db.String(100), nullable=False)
    
    # --- البيانات الجغرافية والاتصال ---
    # ملاحظة: تعتمد العمليات في الخوخة، عدن، المخاء، وحيس على هذه البيانات
    province = db.Column(db.String(100), nullable=False)
    district = db.Column(db.String(100), nullable=False)
    address_detail = db.Column(db.String(500), nullable=False)
    phone = db.Column(db.String(20), nullable=False) # طول مرن للمفاتيح الدولية

    # --- الربط المالي والسيادي ---
    # يعكس هذا القسم رؤية "محجوب أونلاين" لبناء النجاح على الثقة والأنظمة الرقمية
    # e_wallet هنا يمثل "رقم المحفظة السيادي" المولد تلقائياً
    e_wallet = db.Column(db.String(100), unique=True, nullable=False)
    fin_type = db.Column(db.String(50), default='banks') # تصنيف: بنوك أو شركات صرافة
    bank_name = db.Column(db.String(150), nullable=False) # اسم البنك أو شركة الصرافة المختارة
    bank_acc = db.Column(db.String(100), nullable=False) # رقم الحساب المالي للمورد

    # --- بيانات النظام ---
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # يتم التفعيل تلقائياً عند إتمام "التعميد" من لوحة الإدارة
    is_verified = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<Vendor {self.trade_name} - Sovereign ID: {self.e_wallet}>"
