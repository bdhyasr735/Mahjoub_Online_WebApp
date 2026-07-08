# coding: utf-8
# 📂 apps/models/__init__.py

"""
مركز التحكم في الموديلات (Model Registry)
تم ترتيب الاستيراد لضمان تحميل الموديلات الأم قبل التابعة 
لتجنب أخطاء الاعتمادات الدائرية (Circular Imports).
"""

# استيراد قاعدة البيانات لتكون متاحة عبر apps.models
from apps.extensions import db

# 1. الموديلات الأساسية
from .supplier_db import Supplier
from .admin_db import AdminUser
from .marketer_db import Marketer
from .exchange_db import ExchangeRate

# 2. الموديلات التابعة
from .admin_staff_db import AdminStaff
from .supplier_profile_db import SupplierProfile
from .supplier_staff_db import SupplierStaff
from .wallet_db import SupplierWallet, WalletTransaction
from .financials_db import OrderFinancial
from .orders_db import Order
from .order_items_db import OrderItem
from .sync_log import SyncLog

# 3. القائمة المصدرة (Export Registry)
__all__ = [
    'db',              # تمت إضافة قاعدة البيانات هنا
    'AdminStaff',
    'AdminUser',
    'ExchangeRate',
    'Marketer',
    'Order',
    'OrderItem',
    'OrderFinancial',
    'Supplier',
    'SupplierProfile',
    'SupplierStaff',
    'SupplierWallet',
    'SyncLog',
    'WalletTransaction'
]
