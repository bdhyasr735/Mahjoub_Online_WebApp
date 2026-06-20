# coding: utf-8
# 📂 apps/models/__init__.py - الموزع المركزي للنماذج بنظام التعجيل وحماية السياق

# مصفوفة النماذج المتاحة للوصول الخارجي (تمت إضافة SupplierProfile لتوحيد حوكمة الكيانات)
__all__ = [
    'AdminUser', 'ExchangeRate', 'FinancialLog', 'Supplier', 'SupplierProfile',
    'AdminVault', 'VaultTransaction', 'SupplierWallet', 
    'WalletTransaction', 'ProcessedOrder', 'OrderItem', 'SyncLog'
]

def __getattr__(name):
    """
    آلية التعجيل وحوكمة التوزيع:
    لا يتم استيراد أي نموذج إلا عند طلبه برمجياً في الأكواد لخنق الاستدعاء الدائري كلياً.
    """
    if name == 'AdminUser':
        from .admin_db import AdminUser
        return AdminUser
    elif name == 'ExchangeRate':
        from .financial_db import ExchangeRate
        return ExchangeRate
    elif name == 'FinancialLog':
        from .financial_db import FinancialLog
        return FinancialLog
    elif name == 'Supplier':
        from .supplier_db import Supplier
        return Supplier
    elif name == 'SupplierProfile':
        # 🔗 حقن الكيان التجاري المتقدم لتكتمل الحوكمة مع جدول الحساب الموحد
        from .supplier_profile_db import SupplierProfile
        return SupplierProfile
    elif name == 'AdminVault':
        from .vault_db import AdminVault
        return AdminVault
    elif name == 'VaultTransaction':
        from .vault_db import VaultTransaction
        return VaultTransaction
    elif name == 'SupplierWallet':
        from .wallet_db import SupplierWallet
        return SupplierWallet
    elif name == 'WalletTransaction':
        from .wallet_db import WalletTransaction
        return WalletTransaction
    elif name == 'ProcessedOrder':
        from .orders_db import ProcessedOrder
        return ProcessedOrder
    elif name == 'OrderItem':
        from .orders_db import OrderItem
        return OrderItem
    elif name == 'SyncLog':
        from .sync_log import SyncLog
        return SyncLog
        
    raise AttributeError(f"الموديل '{name}' غير معرف في حوكمة النماذج المركزية.")
