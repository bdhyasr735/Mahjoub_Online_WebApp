# -*- coding: utf-8 -*-
from flask import Blueprint

suppliers_auth_bp = Blueprint(
    'suppliers_auth_bp',
    __name__,
    template_folder='templates',
    static_folder='static'
    # ✅ تم إزالة url_prefix من هنا
)

from apps.suppliers_auth_portal import routes
