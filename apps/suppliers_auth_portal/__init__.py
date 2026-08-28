# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/__init__.py

from flask import Blueprint

# ✅ تغيير: استخدام نفس اسم Blueprint الموجود في routes.py
suppliers_auth_bp = Blueprint(
    'suppliers_auth_bp',  # ← نفس الاسم في routes.py
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/suppliers/static',
    url_prefix='/suppliers'  # ← نفس المسار في routes.py
)

# الاستيراد المؤجل (Lazy Import) لمنع خطأ الاستيراد الدائري
from apps.suppliers_auth_portal import routes
