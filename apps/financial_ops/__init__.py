import os
from flask import Blueprint

# تحديد المسار المطلق لمجلد القوالب لضمان استقلاليته عن أي شيء آخر
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

wallet_blueprint = Blueprint(
    'wallet', 
    __name__, 
    template_folder=template_dir  # المسار المطلق يضمن عدم ضياع Flask
)
