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
# تم تعديل الاستيراد ليتوافق مع أسماء ملفات الترسانة الحالية
from . import routes                # محرك Dashboard والإحصائيات
from . import auth                  # محرك الحماية والولوج
from . import add_supplier_routes    # محرك نافذة الموردين (المحرك الذي أرسلته لي)

# مستقبلاً: أي نافذة جديدة (مناديب، مخازن) تضاف هنا بسطر واحد
# from . import manage_delivery

"""
تنبيه للمؤسس علي محجوب:
تم تحديث الربط ليعمل مع 'add_supplier_routes.py'. 
الآن الترسانة ستتعرف على مسارات الموردين وتعمل دون أخطاء 'Crashed'.
"""
