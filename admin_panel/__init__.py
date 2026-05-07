# admin_panel/__init__.py
from flask import Blueprint

# 1. إعلان الهوية السيادية لمنطقة الإدارة (Blueprint Definition)
# تم تحديد مجلدات القوالب والملفات الثابتة لضمان عزل بيئة الإدارة عن الواجهة العامة.
# إضافة url_prefix تجعل كل الروابط تبدأ بـ /admin (مثلاً: /admin/manage-suppliers)
admin_bp = Blueprint(
    'admin', 
    __name__, 
    template_folder='templates',
    static_folder='static',
    url_prefix='/admin' 
)

# 2. بروتوكول كسر التداخل (Circular Import Protection)
# استيراد المكونات بعد تعريف Blueprint يضمن أن Flask يرى 'admin_bp' أولاً قبل تشغيل المسارات.
# ملاحظة: تم دمج منطق 'manage_suppliers' داخل 'routes' لتبسيط الهيكلية ورفع الأداء.
from . import routes           # المسارات الرئيسية، الـ Dashboard، والـ API السيادي
from . import auth             # نظام تسجيل الدخول والتحقق من هوية المؤسس علي محجوب

# 3. بروتوكول الحماية والإدارة
# يتم هنا استيراد أي أدوات مساعدة خاصة بالإدارة فقط لضمان خصوصية النظام.

"""
ملاحظة سيادية للمؤسس علي:
تأكد من تسجيل هذا الـ Blueprint في ملف التطبيق الرئيسي (app.py أو core/__init__.py) 
عبر الكود التالي لكي تعمل الترسانة:

from admin_panel import admin_bp
app.register_blueprint(admin_bp)
"""
