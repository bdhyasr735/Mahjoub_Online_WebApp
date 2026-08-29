# -*- coding: utf-8 -*-
from flask import Blueprint

suppliers_auth_bp = Blueprint(
    'suppliers_auth_bp',
    __name__,
    template_folder='templates',
    static_folder='static'
    # ✅ بدون url_prefix هنا
)

from apps.suppliers_auth_portal import routes
