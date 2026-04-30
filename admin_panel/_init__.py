from flask import Blueprint

# تعريف البلوبرنت وتحديد مجلد القوالب
admin_panel = Blueprint(
    'admin_panel', 
    __name__, 
    template_folder='templates'
)

# استيراد المسارات بعد تعريف البلوبرنت لتجنب الخطأ الدائري
from . import routes
