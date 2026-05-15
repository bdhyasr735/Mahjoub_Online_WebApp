# coding: utf-8
# 🌟 استيراد كائن قاعدة البيانات المشترك لضمان تكامل الجداول السيادية
from models.admin_db import db
from datetime import datetime

class Supplier(db.Model):
    """
    🛡️ الموديل السيادي المعتمد لتخزين بيانات الموردين - منصة محجوب أونلاين 2026
    تم تصميمه ليدعم التوثيق الكامل والربط المالي الدقيق.
    """
    __tablename__ = 'suppliers'

    # 🔑 المعرفات الأساسية (Primary Keys)
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sovereign_id = db.Column(db.String(50), unique=True, nullable=False)  # المعرف الموحد SUP-WEL-...
    
    # 🔐 بيانات الوصول والتوثيق
    # ملاحظة للمؤسس: يدعم اسم المستخدم باللغة العربية بفضل ترميز قاعدة البيانات UTF-8
    username = db.Column(db.String(50), unique=True, nullable=False)     # اسم المستخدم
    password = db.Column(db.String(255), nullable=False)                  # كلمة المرور
    
    # 🪪 بيانات التوثيق الرسمية (تمت إضافتها لتطابق ملف الـ HTML)
    identity_type = db.Column(db.String(100), nullable=True)             # نوع الهوية (بطاقة، سجل تجاري..)
    identity_number = db.Column(db.String(100), nullable=True)           # رقم الهوية المرفوعة
    
    # 🏢 بيانات المنشأة والنشاط التجاري
    owner_name = db.Column(db.String(150), nullable=False)                # اسم المالك الكامل
    owner_phone = db.Column(db.String(20), nullable=True)                 # رقم هاتف المالك الشخصي
    trade_name = db.Column(db.String(150), unique=True, nullable=False)   # الاسم التجاري للمحل/المنشأة
    business_type = db.Column(db.String(100), nullable=True)              # نوع النشاط التجاري
    shop_phone = db.Column(db.String(20), nullable=False)                 # رقم هاتف المحل
    
    # 📍 الجغرافيا والعناوين السيادية
    province = db.Column(db.String(100), nullable=False)                  # المحافظة
    district = db.Column(db.String(100), nullable=False)                  # المديرية
    address_detail = db.Column(db.Text, nullable=False)                   # العنوان بالتفصيل
    
    # 💰 الربط المالي السيادي
    finance_type = db.Column(db.String(50), nullable=False)               # نوع الربط (بنوك / صرافة)
    bank_name = db.Column(db.String(150), nullable=False)                 # جهة التحويل (اسم البنك أو الصراف)
    bank_account = db.Column(db.String(100), nullable=False)              # رقم الحساب / السحاب البنكي
    category = db.Column(db.String(50), nullable=False)                   # فئة المورد (جملة / تجزئة)
    
    # 📅 الأرشفة والوقت
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        """تمثيل نصي للمورد يسهل عملية التتبع في سجلات النظام"""
        return f"<Supplier {self.trade_name} - {self.sovereign_id}>"
