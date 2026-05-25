# coding: utf-8
import os
from flask import Blueprint

# تحديد المسار المطلق لمجلد القوالب لضمان استقلاليته
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

# تغيير اسم البلوبرينت ليطابق الاسم الجديد
financial_blueprint = Blueprint(
    'financial_ops', 
    __name__, 
    template_folder=template_dir 
)
