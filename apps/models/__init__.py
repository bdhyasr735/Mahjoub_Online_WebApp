# coding: utf-8
# 📂 apps/models/__init__.py

"""
مركز التحكم في الموديلات (Model Registry)
تنبيه: ترتيب الاستيراد هنا يضمن تهيئة الموديلات (Declaration) 
بالتسلسل الصحيح لتجنب أخطاء العلاقات (Foreign Key Constraints).
"""

# أولاً: الموديلات الأساسية (التي لا تعتمد على غيرها)
from .supplier_db import Supplier
from .admin_db import AdminUser
from .marketer_db import Marketer
from .sync_log import SyncLog

# ثانياً: الموديلات المعتمدة (التي تحتوي على Foreign Keys وترتبط بالأساسية)
from .admin_staff_db import AdminStaff
from .supplier_staff_db import SupplierStaff
from .supplier_profile_db import SupplierProfile
from .wallet_db import SupplierWallet
from .orders_db import Order
from .financials_db import OrderFinancial

# القائمة الموحدة للتصدير (لضمان توفرها عند الاستدعاء من أي مكان في التطبيق)
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
