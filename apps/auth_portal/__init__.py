# coding: utf-8
# 📂 apps/auth_portal/__init__.py - تعريف بوابة الدخول

from flask import Blueprint

# تعريف الـ Blueprint الخاص ببوابة الدخول
auth_portal = Blueprint(
    'auth_portal', 
    __name__, 
    template_folder='templates',
    static_folder='static'
)

# استيراد المسارات لضمان تسجيلها عند تحميل الـ Blueprint
from . import routes
