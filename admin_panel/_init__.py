from flask import Blueprint

# 1. تعريف البلوبرينت السيادي للإدارة
# قمنا بتحديد template_folder لكي يقرأ ملفات الـ HTML من داخل مجلد templates الخاص به
admin_bp = Blueprint(
    'admin_panel', 
    __name__, 
    template_folder='templates'
)

# 2. استيراد الروابط (Routes) بعد تعريف البلوبرينت لمنع الخطأ الدوري (Circular Import)
from . import routes
