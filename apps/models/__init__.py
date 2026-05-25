# coding: utf-8
# 📂 apps/models/__init__.py
# تجميع وإشهار النماذج لسهولة الاستيراد من خارج حزمة models

from apps.models.admin_db import AdminUser
from apps.models.supplier_db import Supplier

# استيراد موديلات المحفظة وإشهارها باسم 'Wallet' لتتوافق مع طلبات الاستيراد في routes.py
from apps.models.wallet_db import SupplierWallet as Wallet, WalletTransaction

# إشهار موديل التسويات الإدارية
from apps.models.settlements_db import AdminSettlement

# إضافة إشهار موديل كشف الحساب الجديد
from apps.models.statement_db import SupplierStatement

# تحديث __all__ لضمان وصول النظام لجميع الموديلات عند الاستيراد الجماعي
__all__ = [
    'AdminUser',
    'Supplier',
    'Wallet',
    'WalletTransaction',
    'AdminSettlement',
    'SupplierStatement'
]
