# coding: utf-8
# 📂 apps/models/__init__.py - حوكمة النماذج المركزية (التحميل المباشر)

from .admin_db import AdminUser
from .financial_db import ExchangeRate, FinancialLog
from .supplier_db import Supplier
from .supplier_profile_db import SupplierProfile
from .vault_db import AdminVault, VaultTransaction
from .wallet_db import SupplierWallet, WalletTransaction
from .orders_db import ProcessedOrder, OrderItem
from .sync_log import SyncLog
from .otp_db import OTPLog  # <--- إضافة مهمة لتوثيق الـ OTP والواتساب

__all__ = [
    'AdminUser', 'ExchangeRate', 'FinancialLog', 'Supplier', 'SupplierProfile',
    'AdminVault', 'VaultTransaction', 'SupplierWallet', 
    'WalletTransaction', 'ProcessedOrder', 'OrderItem', 'SyncLog', 'OTPLog' # <--- لا تنسَ إضافتها هنا
]
