# coding: utf-8
from flask import Blueprint
import os

# تحديد المسار للقوالب
current_dir = os.path.dirname(os.path.abspath(__file__))
template_path = os.path.join(current_dir, 'templates')

# تعريف الـ Blueprint باسم 'admin_dashboard' ليتطابق مع الاستدعاءات
admin_dashboard = Blueprint(
    'admin_dashboard', 
    __name__, 
    template_folder='templates'
)

# استيراد المسارات لربطها بالـ Blueprint
from . import routes
