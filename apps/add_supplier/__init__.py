# coding: utf-8
from flask import Blueprint
import os

# 1. تحديد المسار المطلق لضمان عمل المجلدات في بيئة Railway السحابية
current_dir = os.path.dirname(os.path.abspath(__file__))
template_path = os.path.join(current_dir, 'templates')
static_path = os.path.join(current_dir, 'static')

# 2. تعريف البلوبرينت مع المسارات الدقيقة
admin_suppliers = Blueprint(
    'admin_suppliers', 
    __name__,
    template_folder=template_path, # استخدام المسار المطلق
    static_folder=static_path      # استخدام المسار المطلق للملفات الثابتة
)

# 3. ربط المسارات (Routes) بعد تعريف البلوبرينت لضمان الاستقرار
from . import routes
