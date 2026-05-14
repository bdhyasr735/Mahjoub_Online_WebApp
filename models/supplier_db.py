from apps import db
from datetime import datetime

class Supplier(db.Model):
    """
    🛡️ الموديل السيادي المعتمد لتخزين بيانات الموردين - منصة محجوب أونلاين 2026
    """
    __tablename__ = 'suppliers'

    # 🔑 المعرفات الأساسية
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sovereign_id = db.Column(db.String(50), unique=True, nullable=False)  # المعرف الموحد SUP-WEL-...
    
    # 🔐 بيانات الوصول والتوثيق
    username = db.Column(db.String(50), unique=True, nullable=False)     # اسم المستخدم
    password = db.Column(db.String(255), nullable=False)                  # كلمة المرور
    
    # 🏢 بيانات المنشأة والنشاط التجاري
    owner_name = db.Column(db.String(150), nullable=False)                # اسم المالك الكامل
    trade_name = db.Column(db.String(150), unique=True, nullable=False)   # الاسم التجاري للمحل/المنشأة
    business_type = db.Column(db.String(100), nullable=True)             # 🌟 نوع النشاط التجاري المضاف حديثاً
    shop_phone = db.Column(db.String(20), nullable=False)                 # رقم هاتف المحل
    
    # 📍 الجغرافيا والعناوين
    province = db.Column(db.String(100), nullable=False)                  # المحافظة
    district = db.Column(db.String(100), nullable=False)                  # المديرية
    address_detail = db.Column(db.Text, nullable=False)                   # العنوان بالتفصيل
    
    # 💰 الربط المالي والفئات
    finance_type = db.Column(db.String(50), nullable=False)               # نوع الربط (بنوك / صرافة)
    bank_name = db.Column(db.String(150), nullable=False)                 # جهة التحويل (اسم البنك أو الصراف)
    bank_account = db.Column(db.String(100), nullable=False)              # رقم الحساب / السحاب البنكي
    category = db.Column(db.String(50), nullable=False)                   # فئة المورد (جملة / تجزئة)
    
    # 📅 الأرشفة والوقت
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Supplier {self.trade_name} - {self.sovereign_id}>"
