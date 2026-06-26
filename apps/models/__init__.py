# coding: utf-8
# 📂 apps/models/__init__.py

"""
مركز التحكم في الموديلات (Model Registry)
تنبيه: تم ترتيب الاستيراد لضمان تعيين العلاقات (Relationships) 
بشكل صحيح في بيئة SQLAlchemy Registry.
"""

# 1. الموديلات الأساسية (التي تعتمد عليها باقي الجداول)
from .supplier_db import Supplier
from .orders_db import Order

# 2. الموديلات المرتبطة
from .admin_db import AdminUser
from .admin_staff_db import AdminStaff
from .supplier_staff_db import SupplierStaff
from .supplier_profile_db import SupplierProfile
from .wallet_db import SupplierWallet
from .financials_db import OrderFinancial
from .marketers_db import Marketer
from .sync_log import SyncLog

# القائمة الموحدة للتصدير - تضمن وصول SQLAlchemy لكل الموديلات عند استخدام db.Model
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
