from flask import Blueprint

# تعريف البلوبرنت
admin_panel = Blueprint('admin_panel', __name__, template_folder='templates')

# استيراد المسارات بعد تعريف البلوبرنت لتجنب التداخل
from . import routes
