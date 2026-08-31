# -*- coding: utf-8 -*-
# 📂 apps/auth_portal/__init__.py

from flask import Blueprint

auth_bp = Blueprint(
    'auth',
    __name__,
    template_folder='templates',
    static_folder='static'
)

from apps.auth_portal import routes
