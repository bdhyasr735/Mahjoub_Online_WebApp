# coding: utf-8
# 🛡️ تعريف المسارات السيادية للوحة التحكم

from flask import Blueprint
import os

# تعريف الـ Blueprint مع تحديد مجلد القوالب بدقة
admin_dashboard = Blueprint(
    'admin_dashboard', 
    __name__, 
    template_folder='templates'
)

# استيراد الـ routes هنا ضروري لربط المسارات بالـ Blueprint
from . import routes
