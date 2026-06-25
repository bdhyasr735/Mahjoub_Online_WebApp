# coding: utf-8
# 📂 apps/models/__init__.py

from .admin_db import AdminUser
from .admin_staff_db import AdminStaff
from .financials_db import OrderFinancial
from .marketers_db import Marketer
from .orders_db import Order
from .supplier_db import Supplier
from .supplier_profile_db import SupplierProfile
from .supplier_staff_db import SupplierStaff
from .sync_log import SyncLog
from .wallet_db import SupplierWallet  # تم تحديث الاسم ليكون SupplierWallet

# القائمة الموحدة للتصدير (Export)
__all__ = [
    'Supplier', 
    'AdminUser', 
    'AdminStaff', 
    'Marketer', 
    'SupplierProfile', 
    'SupplierStaff', 
    'SyncLog', 
    'SupplierWallet',  # تم تحديث الاسم هنا أيضاً
    'Order', 
    'OrderFinancial'
]
