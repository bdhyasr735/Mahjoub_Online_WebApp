# -*- coding: utf-8 -*-
# 📂 apps/supplier_permissions/__init__.py

from flask import Blueprint

supplier_perms_bp = Blueprint(
    'supplier_perms',
    __name__,
    template_folder='templates',
    url_prefix='/supplier/permissions'
)

from . import routes
