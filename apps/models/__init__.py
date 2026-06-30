# coding: utf-8
# 📂 apps/models/__init__.py

"""
مركز التحكم في الموديلات (Model Registry)
يضمن هذا الملف أن جميع الموديلات يتم تسجيلها في SQLAlchemy 
قبل أي عملية اتصال بقاعدة البيانات.
"""

from .admin_db import AdminUser
from .admin_staff_db import AdminStaff
from .financials_db import OrderFinancial
from .marketer_db import Marketer
from .orders_db import Order
from .supplier_db import Supplier
from .supplier_profile_db import SupplierProfile
from .supplier_staff_db import SupplierStaff
from .wallet_db import SupplierWallet, WalletTransaction
from .sync_log import SyncLog

__all__ = [
    'AdminStaff',
    'AdminUser',
    'Marketer',
    'Order',
    'OrderFinancial',
    'Supplier',
    'SupplierProfile',
    'SupplierStaff',
    'SupplierWallet',
    'SyncLog',
    'WalletTransaction'
]
