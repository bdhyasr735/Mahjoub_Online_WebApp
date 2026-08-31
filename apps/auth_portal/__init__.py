# -*- coding: utf-8 -*-
# 📂 apps/auth_portal/__init__.py

from flask import Blueprint

# تعريف البلايبوينت الخاصة ببوابة المصادقة الإدارية
auth_bp = Blueprint(
    'auth_bp',
    __name__,
    template_folder='templates',
    static_folder='static'
)

# استيراد المسارات لضمان تسجيلها داخل البلايبوينت
from apps.auth_portal import routes
