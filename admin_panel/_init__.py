from flask import Blueprint

# تعريف الكائن أولاً
admin_panel = Blueprint('admin_panel', __name__, template_folder='templates')

# الاستيراد في الأسفل لتجنب التعليق الدائري
from . import routes
