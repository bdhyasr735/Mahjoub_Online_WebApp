# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/__init__.py

from flask import Blueprint

suppliers_bp = Blueprint(
    'suppliers_auth_portal',
    __name__,
    template_folder='templates',
    static_folder='static'
)

# الاستيراد المؤجل (Lazy Import) لمنع خطأ الاستيراد الدائري
from apps.suppliers_auth_portal import routes
