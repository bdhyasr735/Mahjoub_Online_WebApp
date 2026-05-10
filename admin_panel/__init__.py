# admin_panel/__init__.py
from flask import Blueprint

# 1. إعلان الهوية السيادية لمنطقة الإدارة
admin_bp = Blueprint(
    'admin', 
    __name__, 
    template_folder='templates', 
    static_folder='static', 
    url_prefix='/admin' 
)

# 2. بروتوكول الربط السيادي (Sovereign Linkage)
# هنا نقوم بتفعيل المحركات بشكل منفصل تماماً لضمان عدم تضخم ملف الـ routes
from . import routes            # خاص بـ Dashboard والإحصائيات العامة فقط
from . import auth              # خاص بوابات الدخول والحماية
from . import manage_suppliers   # محرك إدارة الموردين (منفصل تماماً)

# مستقبلاً: أي نافذة جديدة تضاف هنا بسطر واحد فقط
# from . import manage_warehouse 

"""
تنبيه للمؤسس علي محجوب:
بهذا التقسيم، لن تحتاج أبداً لفتح ملف routes.py لتعديل كود الموردين.
لقد تم كسر "التداخل" بجعل كل قطة من الترسانة تعمل في محركها الخاص.
"""
