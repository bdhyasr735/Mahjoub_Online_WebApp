# coding: utf-8
# 📂 apps/models/__init__.py - حوكمة النماذج المركزية

from .admin_db import AdminUser
from .financial_db import ExchangeRate, FinancialLog
from .supplier_db import Supplier
from .supplier_profile_db import SupplierProfile
from .vault_db import AdminVault, VaultTransaction
from .wallet_db import SupplierWallet, WalletTransaction
from .orders_db import ProcessedOrder, OrderItem
from .sync_log import SyncLog
from .otp_db import OTPVerification
from .marketer_db import Marketer  # تمت إضافته ليعالج خطأ النظام

__all__ = [
    'AdminUser', 
    'ExchangeRate', 
    'FinancialLog', 
    'Supplier', 
    'SupplierProfile',
    'AdminVault', 
    'VaultTransaction', 
    'SupplierWallet', 
    'WalletTransaction', 
    'ProcessedOrder', 
    'OrderItem', 
    'SyncLog', 
    'OTPVerification',
    'Marketer'  # تمت إضافته للقائمة ليصبح مرئياً للنظام
]
