# apps/admin_dashboard/__init__.py
from flask import Blueprint
import os

# تعريف الـ Blueprint بالاسم 'admin_dashboard'
admin_dashboard = Blueprint(
    'admin_dashboard', 
    __name__, 
    template_folder='templates'
)

# استيراد المسارات (Routes) بعد تعريف الـ Blueprint لتجنب التداخل
from . import routes
