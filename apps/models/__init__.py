# coding: utf-8
# 📂 apps/models/__init__.py

"""
مركز التحكم في الموديلات (Model Registry)
تنبيه: تم ترتيب الاستيراد لضمان تهيئة الموديلات بالتسلسل الصحيح للعلاقات.
"""

# أولاً: الموديلات الأساسية (التي لا تعتمد على غيرها)
from .supplier_db import Supplier
from .admin_db import AdminUser
from .marketer_db import Marketer
from .sync_log import SyncLog

# ثانياً: الموديلات المعتمدة (التي تحتوي على Foreign Keys)
from .admin_staff_db import AdminStaff
from .supplier_staff_db import SupplierStaff
from .supplier_profile_db import SupplierProfile

# ثالثاً: موديلات المحفظة (الارتباط بين المحفظة والحركات)
from .wallet_db import SupplierWallet, WalletTransaction

# رابعاً: الموديلات المرتبطة بالطلبات والماليات
from .orders_db import Order
from .financials_db import OrderFinancial

# القائمة الموحدة للتصدير
__all__ = [
    'AdminUser',
    'AdminStaff',
    'Supplier',
    'SupplierStaff',
    'SupplierProfile',
    'SupplierWallet',
    'WalletTransaction', # إضافة الموديل الجديد هنا
    'Order',
    'OrderFinancial',
    'Marketer',
    'SyncLog'
]
