from flask import Blueprint

# قمنا بتغيير اسم المتغير البرمجي إلى admin_blueprint 
# لكي لا يختلط الأمر على بايثون بين اسم "المجلد" واسم "الكائن"
admin_blueprint = Blueprint('admin_panel', __name__, template_folder='templates')

# استدعاء المسارات لربطها بالبلوبرنت المسمى حديثاً
from . import routes
