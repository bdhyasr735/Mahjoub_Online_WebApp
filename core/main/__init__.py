from flask import Blueprint

# 1. إنشاء البلوبرنت (Blueprint)
# هذا السطر يعرّف "هوية" الجزء الرئيسي للمتجر ويحدد مجلد القوالب (templates)
main_bp = Blueprint('main', __name__, template_folder='templates')

# 2. ربط المسارات (Routes)
# نقوم باستيراد ملف routes هنا (في الأسفل) لتجنب مشكلة "التضارب الدائري"
# لكي يتم تسجيل جميع الروابط (مثل الصفحة الرئيسية والمتجر) تحت هذا البلوبرنت
from . import routes
