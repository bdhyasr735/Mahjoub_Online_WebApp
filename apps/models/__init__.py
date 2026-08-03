# coding: utf-8
# 📂 apps/models/__init__.py

"""
مركز التحكم في الموديلات (Model Registry)
"""

from apps.extensions import db

# استخدام الاستيراد المطلق (Absolute Imports) حصرياً لمنع ازدواجية تسجيل الموديلات في ذاكرة SQLAlchemy
from apps.models.supplier_db import Supplier
from apps.models.admin_db import AdminUser
from apps.models.marketer_db import Marketer
from apps.models.admin_staff_db import AdminStaff
from apps.models.supplier_profile_db import SupplierProfile
from apps.models.supplier_staff_db import SupplierStaff
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from apps.models.financials_db import OrderFinancial
from apps.models.orders_db import Order, OrderItem
from apps.models.product_db import Product
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.models.sync_log import SyncLog

# القائمة المصدرة (Export Registry)
__all__ = [
    'db',
    'AdminStaff',
    'AdminUser',
    'Marketer',
    'Order',
    'OrderItem',
    'OrderFinancial',
    'Product',
    'ProductSupplierMapping',
    'Supplier',
    'SupplierProfile',
    'SupplierStaff',
    'SupplierWallet',
    'SyncLog',
    'WalletTransaction'
]
