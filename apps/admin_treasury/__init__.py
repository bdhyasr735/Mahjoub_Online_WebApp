# -*- coding: utf-8 -*-
# 📂 apps/admin_treasury/__init__.py

from flask import Blueprint

admin_treasury_bp = Blueprint(
    'admin_treasury',
    __name__,
    template_folder='templates',
    static_folder='static'
)

try:
    from apps.admin_treasury.routes import treasury_controller
except ImportError as e:
    print(f"[!] Warning: Could not import treasury controllers: {e}")
