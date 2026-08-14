# -*- coding: utf-8 -*-
# 📂 apps/admin_treasury/__init__.py

from flask import Blueprint

# تعريف البلوبرنت هنا وربطه بالـ url_prefix الصحيح
admin_treasury_bp = Blueprint(
    'admin_treasury',
    __name__,
    template_folder='templates',
    static_folder='static',
    url_prefix='/admin/treasury'
)

# استيراد المتحكمات لترتبط بالبلوبرنت
from apps.admin_treasury.routes import treasury_controller
