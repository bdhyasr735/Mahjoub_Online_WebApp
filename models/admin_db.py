# coding: utf-8
# 🌟 استيراد المكتبات اللازمة لبناء نظام مستخدمين آمن
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# 🗄️ تعريف كائن قاعدة البيانات المركزي (يجب ربطه بـ app في ملف run.py)
db = SQLAlchemy()

class AdminUser(db.Model, UserMixin):
    """
    موديل المسؤولين (AdminUser): 
    هذا الكلاس يمثل جدول المسؤولين في قاعدة البيانات ويتحكم في صلاحيات الدخول.
    """
    __tablename__ = 'admin_users'

    # 🆔 الحقول الأساسية للهوية الرقمية
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False) # اسم المستخدم (فريد)
    email = db.Column(db.String(120), unique=True, nullable=False)    # البريد الإلكتروني
    password_hash = db.Column(db.String(255), nullable=False)        # كلمة المرور المشفرة
    
    # 👤 بيانات التعريف والمهام
    full_name = db.Column(db.String(100), nullable=True)             # الاسم الكامل
    role = db.Column(db.String(20), default='super_admin')           # الرتبة أو الصلاحية
    
    # 🕒 سجلات النشاط الزمني
    # ملاحظة: تم استخدام utcnow() لتسجيل التوقيت العالمي (يظهر في سجلات Railway)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        """
        دالة التشفير: تأخذ كلمة المرور العادية وتحولها إلى رمز معقد (Hash) 
        لحمايتها من الاختراق.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        دالة التحقق: تقارن كلمة المرور التي يدخلها المستخدم مع الرمز المشفر المخزن.
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        """
        طريقة عرض الكائن برمجياً عند الطباعة أو في سجلات النظام.
        """
        return f'<AdminUser {self.username}>'
