from flask import Blueprint

# إنشاء البلوبرينت أولاً
admin_dashboard = Blueprint('admin_dashboard', __name__, template_folder='templates')

# استيراد المسارات في نهاية الملف لمنع التضارب (Circular Import)
from . import routes
