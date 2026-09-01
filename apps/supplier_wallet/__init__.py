# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/__init__.py
# حزمة محفظة الموردين (Supplier Wallet Package)

"""
حزمة محفظة الموردين
توفر إدارة المحفظة المالية للموردين، بما في ذلك:
- عرض الرصيد
- سحب الأرباح
- كشف الحساب
- إدارة طلبات السحب
"""

from flask import Blueprint
from apps.supplier_wallet.registry import register_module, LINKS, MENU_ITEMS, MODULE_NAME, MODULE_ICON

__version__ = '1.0.0'
__all__ = [
    'register_module',
    'LINKS',
    'MENU_ITEMS',
    'MODULE_NAME',
    'MODULE_ICON',
    'wallet_bp'
]

# ✅ تعريف الـ Blueprint هنا أيضاً للتأكد من وجوده
try:
    from apps.supplier_wallet.routes import wallet_bp
except ImportError as e:
    print(f"⚠️ [تحذير]: فشل استيراد wallet_bp من routes.py - {str(e)}")
    # إنشاء Blueprint مؤقت إذا لم يتم استيراده
    wallet_bp = Blueprint('supplier_wallet', __name__, template_folder='templates', url_prefix='/supplier/wallet')
    print("✅ [__init__]: تم إنشاء Blueprint 'supplier_wallet' بشكل مؤقت.")
