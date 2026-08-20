# -*- coding: utf-8 -*-
from flask import Blueprint

supplier_wallet_bp = Blueprint(
    'supplier_wallet',
    __name__,
    template_folder='templates',
    static_folder='static'
)

# استيراد مجلد المسارات في نهاية الملف لتسجيلها بعد إنشاء الـ Blueprint
from .routes import wallet_routes
