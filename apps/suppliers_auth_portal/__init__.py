# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/__init__.py

from flask import Blueprint

suppliers_bp = Blueprint(
    'suppliers_bp',
    __name__,
    template_folder='templates',
    static_folder='static',
    url_prefix='/supplier'
)

# استيراد الملفات المقسمة لتسجيل المسارات (Routes) تلقائياً داخل الـ Blueprint
from apps.suppliers_auth_portal import auth_login, auth_register, auth_recovery
