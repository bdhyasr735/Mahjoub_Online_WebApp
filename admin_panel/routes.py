from flask import Blueprint

# تعريف البوابة مع تحديد مجلد القوالب
admin_bp = Blueprint('admin_panel', __name__, template_folder='templates')

from . import routes
