# -*- coding: utf-8 -*-
# 📂 apps/suppliers_permissions/__init__.py

from flask import Blueprint

suppliers_permissions_bp = Blueprint(
    'suppliers_permissions_bp',
    __name__,
    template_folder='templates',
    static_folder='static'
)

from apps.suppliers_permissions import routes
