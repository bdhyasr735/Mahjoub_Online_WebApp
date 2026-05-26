from flask import Blueprint

# إعداد الـ Blueprint بالاسم المطابق للمسارات 'statement_blueprint'
statement_blueprint = Blueprint(
    'statement_blueprint', 
    __name__, 
    template_folder='templates'
)

# استيراد المسارات بعد تعريف الـ Blueprint لتفادي الـ Circular Import ولضمان تسجيلها
from apps.statement import routes
