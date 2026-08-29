# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/__init__.py

from flask import Blueprint

# ✅ تعريف الـ Blueprint مع المسار
suppliers_bp = Blueprint(
    'suppliers_auth',
    __name__,
    template_folder='templates',
    static_folder='static'
)

from apps.suppliers_auth_portal import routes
