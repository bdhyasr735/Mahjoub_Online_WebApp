# coding: utf-8
# 📂 apps/models/__init__.py

# نقوم باستيراد النماذج لضمان تهيئتها بواسطة SQLAlchemy
# تم ترتيب الاستيراد لضمان أن الجداول الأساسية (مثل Supplier) 
# معرفة قبل الجداول المرتبطة بها (مثل SupplierStaff, Wallet)

from .admin_db import AdminUser
from .admin_staff_db import AdminStaff
from .supplier_db import Supplier
from .supplier_staff_db import SupplierStaff
from .supplier_profile_db import SupplierProfile
from .wallet_db import SupplierWallet
from .orders_db import Order
from .financials_db import OrderFinancial
from .marketers_db import Marketer
from .sync_log import SyncLog

# القائمة الموحدة للتصدير
__all__ = [
    'AdminUser',
    'AdminStaff',
    'Supplier',
    'SupplierStaff',
    'SupplierProfile',
    'SupplierWallet',
    'Order',
    'OrderFinancial',
    'Marketer',
    'SyncLog'
]
