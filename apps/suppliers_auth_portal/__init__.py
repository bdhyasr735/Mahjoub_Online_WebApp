# -*- coding: utf-8 -*-
from flask import Blueprint

suppliers_bp = Blueprint(
    'suppliers_auth',  # ✅ الاسم الصحيح
    __name__,
    template_folder='templates',
    static_folder='static'
)

from apps.suppliers_auth_portal import routes
