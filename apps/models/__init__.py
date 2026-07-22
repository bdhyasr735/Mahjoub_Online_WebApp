# coding: utf-8
# 📂 apps/models/__init__.py

"""
مركز التحكم في الموديلات (Model Registry)
تنبيه: الترتيب هنا حيوي جداً لتجنب تداخل الـ Mappers. 
تم فصل الموديلات الأساسية عن التابعة التي تحتوي على ForeignKeys.
"""

from apps.extensions import db

# 1. الموديلات الأساسية (مستقلة، لا تعتمد على موديلات أخرى)
from .supplier_db import Supplier
from .admin_db import AdminUser
from .marketer_db import Marketer
# ❌ تم إزالة .exchange_db import ExchangeRate

# 2. الموديلات التابعة (تعتمد على الموديلات الأساسية عبر ForeignKeys)
from .admin_staff_db import AdminStaff
from .supplier_profile_db import SupplierProfile
from .supplier_staff_db import SupplierStaff
from .wallet_db import SupplierWallet, WalletTransaction
from .financials_db import OrderFinancial
from .orders_db import Order
from .order_items_db import OrderItem
from .product_db import Product 
from .product_supplier_map import ProductSupplierMapping  # الموديل الجديد للربط
from .sync_log import SyncLog

# القائمة المصدرة (Export Registry)
__all__ = [
    'db',
    'AdminStaff',
    'AdminUser',
    # ❌ تم إزالة 'ExchangeRate',
    'Marketer',
    'Order',
    'OrderItem',
    'OrderFinancial',
    'Product',
    'ProductSupplierMapping',  # تمت الإضافة
    'Supplier',
    'SupplierProfile',
    'SupplierStaff',
    'SupplierWallet',
    'SyncLog',
    'WalletTransaction'
]
