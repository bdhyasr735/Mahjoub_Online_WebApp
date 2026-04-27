from flask import Blueprint

# تعريف البوابة البرمجية للإدارة
admin_bp = Blueprint(
    'admin_panel', 
    __name__, 
    template_folder='templates',
    static_folder='static'
)

# استيراد المسارات لربطها بالبوابة
from . import routes
