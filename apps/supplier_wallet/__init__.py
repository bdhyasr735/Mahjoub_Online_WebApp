# -*- coding: utf-8 -*-
from flask import Blueprint

# تعريف الـ Blueprint الأساسي للمحفظة
supplier_wallet_bp = Blueprint(
    'supplier_wallet',
    __name__,
    template_folder='templates',
    static_folder='static'
)

# استيراد المسارات لتفعيلها مع الـ Blueprint
from . import wallet_routes
