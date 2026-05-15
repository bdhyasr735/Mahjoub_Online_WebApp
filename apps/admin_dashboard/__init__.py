# coding: utf-8
# 🛡️ وحدة تهيئة لوحة التحكم - محجوب أونلاين 2026

from flask import Blueprint
import os

# 1. تحديد المسارات المطلقة لضمان الاستقرار في بيئة Linux (Railway)
current_dir = os.path.dirname(os.path.abspath(__file__))
# ملاحظة: Flask سيبحث داخل هذا المسار عن المجلدات الفرعية مثل 'admin'
template_path = os.path.join(current_dir, 'templates')

# 2. إنشاء البلوبرينت
# تم استخدام اسم 'admin_dashboard' ليتوافق مع url_for في القالب الملكي
admin_dashboard = Blueprint(
    'admin_dashboard', 
    __name__, 
    template_folder=template_path
)

# 3. استيراد المسارات (Routes) 
# يجب أن يبقى في النهاية لمنع التعارض الدائري (Circular Import)
try:
    from . import routes
    print("✅ تم ربط محرك لوحة التحكم بنجاح.")
except ImportError as e:
    print(f"⚠️ تنبيه: تعذر تحميل مسارات لوحة التحكم: {e}")
