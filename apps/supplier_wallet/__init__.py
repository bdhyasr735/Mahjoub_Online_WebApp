# coding: utf-8
# 📂 apps/supplier_wallet/__init__.py

import logging
from flask import Blueprint

logger = logging.getLogger(__name__)

# 1. إنشاء الـ Blueprint الرئيسي لموديول المحفظة
supplier_wallet_bp = Blueprint(
    'supplier_wallet',
    __name__,
    template_folder='templates',
    static_folder='static'
)

# 2. استيراد حزمة المسارات (routes) لربطها بالـ Blueprint بعد إنشائه مباشرة
try:
    from . import routes
    logger.info("✅ [Supplier Wallet]: تم تحميل مسارات المحفظة بنجاح.")
except Exception as e:
    logger.error(f"❌ [Supplier Wallet]: خطأ أثناء تحميل مسارات المحفظة: {e}")
