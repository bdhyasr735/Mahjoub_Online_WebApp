# -*- coding: utf-8 -*-
from flask import Blueprint

supplier_wallet_bp = Blueprint(
    'supplier_wallet',
    __name__,
    template_folder='templates',
    static_folder='static'
)

# استيراد المسارات في نهاية الملف بعد إنشاء الـ Blueprint تماماً لتجنب أي تعارض
try:
    from apps.supplier_wallet.routes import wallet_routes
except ImportError:
    try:
        from apps.supplier_wallet import wallet_routes
    except ImportError:
        pass
