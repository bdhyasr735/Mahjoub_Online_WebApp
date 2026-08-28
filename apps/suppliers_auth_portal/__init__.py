# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/__init__.py

from flask import Blueprint

# تعريف الـ Blueprint مع إضافة url_prefix اختياري لتوحيد المسارات
suppliers_bp = Blueprint(
    'suppliers_auth_portal',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/suppliers/static',  # إضافة مسار ثابت واضح
    url_prefix='/supplier'  # توحيد جميع المسارات تحت /supplier
)

# الاستيراد المؤجل (Lazy Import) لمنع خطأ الاستيراد الدائري
from apps.suppliers_auth_portal import routes
