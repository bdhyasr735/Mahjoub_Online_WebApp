# coding: utf-8
from flask import Blueprint

# تعريف البلوبرينت
admin_dashboard_bp = Blueprint(
    'admin_dashboard', 
    __name__, 
    template_folder='templates'
)

# استيراد المسارات بعد تعريف البلوبرينت لمنع الخطأ
from . import routes
