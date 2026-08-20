# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/__init__.py

from flask import Blueprint

# 1. تعريف الـ Blueprint الأساسي للمحفظة
supplier_wallet_bp = Blueprint(
    'supplier_wallet',
    __name__,
    template_folder='templates',
    static_folder='static'
)

# 2. استيراد المتحكمات من مجلد/ملف routes.py بالشكل الصحيح لمنع أخطاء الاستيراد
try:
    from apps.supplier_wallet.routes.wallet_routes import *
    # إذا كنت تريد تفعيل مسارات الإدارة أيضاً، يمكنك إلغاء تفعيل السطر التالي:
    # from apps.supplier_wallet.routes.admin_routes import *
except Exception as e:
    print(f"⚠️ [Wallet Init Error]: تعذر استيراد مسارات المحفظة: {e}")
