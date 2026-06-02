# coding: utf-8
# 📂 apps/models/__init__.py
# حزمة الإشهار المركزية لنماذج قاعدة البيانات - منصة محجوب أونلاين 2026

from apps.models.admin_db import AdminUser
from apps.models.supplier_db import Supplier
# تم تحديث الاستيراد ليعكس اسم الكلاس الجديد 'Wallet'
from apps.models.wallet_db import Wallet, WalletTransaction
from apps.models.settlements_db import AdminSettlement
from apps.models.statement_db import SupplierStatement

# القائمة السيادية الحاكمة للاستيراد الخارجي النظيف لمنع تداخل الحزم
__all__ = [
    'AdminUser',
    'Supplier',
    'Wallet',
    'WalletTransaction',
    'AdminSettlement',
    'SupplierStatement'
]
