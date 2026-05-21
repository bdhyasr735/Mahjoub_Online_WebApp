# coding: utf-8
# 🛡️ تعريف المسارات السيادية للوحة التحكم

from flask import Blueprint

# إنشاء الـ Blueprint
admin_dashboard = Blueprint(
    'admin_dashboard', 
    __name__, 
    template_folder='templates'
)

# استيراد الـ routes بعد تعريف الـ Blueprint لتجنب التداخل الحلقي (Circular Import)
from . import routes
